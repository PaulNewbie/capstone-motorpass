# services/license_reader.py
# Refactored for improved accuracy, readability, and offline performance.

import cv2
import numpy as np
import pytesseract
import re
import difflib
import os
import tempfile
import atexit
import time
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date

# Mock hardware functions for standalone testing if needed
# from etc.services.hardware.rpi_camera import *
# from etc.services.hardware.led_control import set_led_white_lighting

# ============== CONFIGURATION ==============

# A single, robust OCR configuration is more reliable than multiple complex ones.
# --psm 6 assumes a single uniform block of text, which is often a good starting point.
OCR_CONFIG_STANDARD = '--psm 6 --oem 3'

CACHE_DIR = "etc/cache/ocr"
MAX_CACHE_FILES = 15

VERIFICATION_KEYWORDS = [
    "REPUBLIC", "PHILIPPINES", "DEPARTMENT", "TRANSPORTATION",
    "LAND TRANSPORTATION OFFICE", "DRIVER'S LICENSE", "DRIVERS LICENSE",
    "LICENSE", "NON-PROFESSIONAL", "PROFESSIONAL", "Last Name", "First Name",
    "Middle Name", "Nationality", "Date of Birth", "Address", "License No",
    "Expiration Date", "EXPIRATION", "ADDRESS"
]

# ============== DATACLASS FOR STRUCTURED RESULTS ==============

@dataclass
class NameInfo:
    """Holds all extracted and verified information from the license."""
    document_type: str
    name: str
    document_verified: str
    formatted_text: str
    expiration_date: Optional[date] = None
    is_expired: Optional[bool] = None
    fingerprint_info: Optional[dict] = None
    match_score: Optional[float] = None

# ============== CACHING SYSTEM (Unchanged) ==============

def _get_cache_key(image_path: str) -> str:
    try:
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return hashlib.md5(image_path.encode()).hexdigest()

def _get_cached_result(image_path: str) -> Optional[str]:
    cache_file = os.path.join(CACHE_DIR, f"{_get_cache_key(image_path)}.txt")
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def _cache_result(image_path: str, text: str):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{_get_cache_key(image_path)}.txt")
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(text)
    _cleanup_old_cache()

def _cleanup_old_cache():
    try:
        cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.txt')]
        if len(cache_files) > MAX_CACHE_FILES:
            cache_files.sort(key=lambda x: os.path.getmtime(os.path.join(CACHE_DIR, x)))
            for old_file in cache_files[:-MAX_CACHE_FILES]:
                os.remove(os.path.join(CACHE_DIR, old_file))
    except:
        pass

# ============== TEMP FILE MANAGEMENT (Unchanged) ==============

_temp_files = []
def register_temp_file(filepath: str):
    if filepath not in _temp_files: _temp_files.append(filepath)

def cleanup_all_temp_files():
    for f in _temp_files[:]: _safe_delete_temp_file(f)

def safe_delete_temp_file(filepath: str):
    _safe_delete_temp_file(filepath)

def _safe_delete_temp_file(filepath: str):
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            if filepath in _temp_files: _temp_files.remove(filepath)
    except: pass
atexit.register(cleanup_all_temp_files)


# ============== HELPER FUNCTIONS ==============

def _check_student_permit(text: str) -> bool:
    """Checks for keywords indicating a student permit."""
    text_upper = text.upper()
    restricted_terms = ["STUDENT PERMIT", "PERMIT NO.", "OR NUMBER", "AMOUNT PAID"]
    return any(term in text_upper for term in restricted_terms)

def _preprocess_image_for_ocr(image_path: str) -> np.ndarray:
    """
    Loads, resizes, and cleans an image to maximize OCR accuracy.
    This is the most critical step for reliable offline performance.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image file: {image_path}")

    # 1. Resize large images to a consistent, manageable width.
    # This improves performance and reduces noise from high-res photos.
    target_width = 1280
    if img.shape[1] > target_width:
        scale = target_width / img.shape[1]
        img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)), interpolation=cv2.INTER_AREA)

    # 2. Convert to grayscale.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Apply CLAHE for contrast enhancement, which is excellent for uneven lighting.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_contrast = clahe.apply(gray)
    
    # 4. Apply a slight bilateral filter to denoise while preserving edges.
    denoised = cv2.bilateralFilter(enhanced_contrast, 9, 75, 75)

    return denoised

def _extract_structured_data(raw_text: str) -> Dict:
    """
    Extracts key information like name and expiration date from the raw OCR text.
    """
    data = {"name": None, "expiration_date": None}
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # --- Find Expiration Date ---
    # Look for the latest valid date in the text, as it will be the expiration date.
    date_pattern = re.compile(r'20\d{2}[-/\s]?\d{2}[-/\s]?\d{2}')
    potential_dates = []
    for line in lines:
        matches = date_pattern.findall(line)
        for match in matches:
            normalized_date = re.sub(r'[-/\s]', '', match)
            try:
                dt = datetime.strptime(normalized_date, "%Y%m%d").date()
                potential_dates.append(dt)
            except ValueError:
                continue
    if potential_dates:
        data["expiration_date"] = max(potential_dates)

    # --- Find Name ---
    # The name usually follows a specific marker line.
    name_markers = ['Last Name. First Name, Middle Name', 'LN.FN.MN', 'LN,FN,MN']
    for i, line in enumerate(lines):
        if any(marker in line for marker in name_markers) and i + 1 < len(lines):
            potential_name = lines[i + 1]
            # A valid name should have a comma and multiple parts.
            if ',' in potential_name and len(potential_name.split()) >= 2:
                # Clean up common OCR errors from the name string.
                clean_name = re.sub(r'[^a-zA-Z\s,]', '', potential_name).strip()
                data["name"] = clean_name.title()
                break # Stop after finding the name
    
    return data


# ============== CORE OCR & VERIFICATION LOGIC ==============

def licenseRead(image_path: str, fingerprint_info: dict) -> NameInfo:
    """
    Performs the full license reading and verification process for a registered user.
    """
    reference_name = fingerprint_info.get('name', 'Unknown')
    
    try:
        # Step 1: Get raw text using Tesseract
        raw_text = _get_cached_result(image_path)
        if not raw_text:
            processed_image = _preprocess_image_for_ocr(image_path)
            raw_text = pytesseract.image_to_string(processed_image, config=OCR_CONFIG_STANDARD)
            _cache_result(image_path, raw_text)

        # Step 2: Check for student permit restriction
        if _check_student_permit(raw_text):
            raise ValueError("STUDENT_PERMIT_DETECTED")

        # Step 3: Extract structured data (name, expiration date)
        extracted_data = _extract_structured_data(raw_text)
        detected_name = extracted_data.get("name")
        expiration_date = extracted_data.get("expiration_date")

        # Step 4: Calculate name similarity score
        sim_score = 0.0
        if detected_name and reference_name:
            clean_detected = re.sub(r'[^A-Z]', '', detected_name.upper())
            clean_reference = re.sub(r'[^A-Z]', '', reference_name.upper())
            sim_score = difflib.SequenceMatcher(None, clean_detected, clean_reference).ratio()
        
        # Step 5: Determine verification status
        keywords_found = sum(1 for kw in VERIFICATION_KEYWORDS if kw in raw_text.upper())
        is_verified = keywords_found >= 3 or sim_score > 0.85
        doc_status = "Driver's License Detected" if is_verified else "Unverified Document"

        # Step 6: Package results into the NameInfo object
        return NameInfo(
            document_type="Driver's License",
            name=detected_name or "Not Found",
            document_verified=doc_status,
            formatted_text=raw_text,
            expiration_date=expiration_date,
            is_expired=expiration_date < date.today() if expiration_date else None,
            fingerprint_info=fingerprint_info,
            match_score=sim_score
        )

    except Exception as e:
        return NameInfo(
            document_type="Error",
            name="Error",
            document_verified="Processing Failed",
            formatted_text=str(e),
            fingerprint_info=fingerprint_info
        )
    finally:
        safe_delete_temp_file(image_path)

def licenseReadGuest(image_path: str) -> NameInfo:
    """
    Simplified license reading for guests.
    """
    try:
        raw_text = _get_cached_result(image_path)
        if not raw_text:
            processed_image = _preprocess_image_for_ocr(image_path)
            raw_text = pytesseract.image_to_string(processed_image, config=OCR_CONFIG_STANDARD)
            _cache_result(image_path, raw_text)
            
        if _check_student_permit(raw_text):
            raise ValueError("STUDENT_PERMIT_DETECTED")

        extracted_data = _extract_structured_data(raw_text)
        detected_name = extracted_data.get("name", "Guest")
        
        return NameInfo(
            document_type="Driver's License",
            name=detected_name,
            document_verified="Document Scanned",
            formatted_text=raw_text
        )
    except Exception as e:
        return NameInfo(
            document_type="Error",
            name="Error",
            document_verified="Processing Failed",
            formatted_text=str(e)
        )
    finally:
        safe_delete_temp_file(image_path)


# ============== VERIFICATION FLOWS ==============

def complete_verification_flow(image_path: str, fingerprint_info: dict, helmet_verified: bool = True) -> bool:
    """
    Checks all conditions for a registered user to be fully verified.
    """
    license_result = licenseRead(image_path, fingerprint_info)

    if "STUDENT_PERMIT" in license_result.formatted_text:
        print("❌ Student Permit detected - Verification FAILED")
        return False
        
    fingerprint_verified = fingerprint_info.get('confidence', 0) > 50
    license_detected = "Driver's License Detected" in license_result.document_verified
    name_matching_verified = (license_result.match_score or 0.0) > 0.85
    license_expiration_valid = license_result.is_expired is False

    # If names match with high confidence, we can be more lenient on keyword detection.
    if name_matching_verified:
        license_detected = True
        print("🎯 Name match override: License detection forced to TRUE")

    all_verified = (helmet_verified and fingerprint_verified and license_detected and name_matching_verified and license_expiration_valid)

    print("\n" + "─" * 50)
    print("🎯 VERIFICATION RESULTS")
    print("─" * 50)
    print(f"🪖 Helmet: {'✅' if helmet_verified else '❌'}")
    print(f"🔒 Fingerprint: {'✅' if fingerprint_verified else '❌'} ({fingerprint_info.get('confidence', 0)}%)")
    print(f"🆔 License Detected: {'✅' if license_detected else '❌'}")
    print(f"👤 Name Match: {'✅' if name_matching_verified else '❌'} ({(license_result.match_score or 0.0) * 100:.1f}%)")
    print(f"📅 License Valid: {'✅' if license_expiration_valid else '❌'}")
    print(f"🟢 STATUS: {'✅ FULLY VERIFIED' if all_verified else '❌ VERIFICATION FAILED'}")
    print("─" * 50 + "\n")

    return all_verified

# (Your camera capture and guest verification flows can remain largely the same,
# but they would call the simplified `licenseRead` and `licenseReadGuest` functions.)

# Example placeholder for camera function if not imported
def auto_capture_license_rpi(*args, **kwargs):
    print("Camera function called (mock).")
    return (None, "camera_error")
