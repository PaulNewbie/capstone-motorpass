# services/license_reader.py - Enhanced with Online/Offline OCR and ROI focus

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
import requests  # Added for online OCR
import socket    # Added for internet connection check
from PIL import Image  # Added for robust image handling with the API
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from etc.services.hardware.rpi_camera import *
from etc.services.hardware.led_control import set_led_white_lighting

# ============== CONFIGURATION ==============

# --- Online OCR Configuration ---
OCR_SPACE_API_KEY = 'K86208907288957'  # Your API key from ocr_project/final_test.py
OCR_SPACE_URL = 'https://api.ocr.space/parse/image'

# --- Offline OCR Configuration ---
OCR_CONFIG_FAST = '--psm 6 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789., '
OCR_CONFIG_STANDARD = '--psm 11 --oem 3'
OCR_CONFIG_DETAILED = '--psm 4 --oem 3'

OPTIMAL_WIDTH, OPTIMAL_HEIGHT = 1280, 960
MIN_WIDTH, MIN_HEIGHT = 640, 480
CACHE_DIR = "etc/cache/ocr"
MAX_CACHE_FILES = 15

VERIFICATION_KEYWORDS = [
    "REPUBLIC", "PHILIPPINES", "DEPARTMENT", "TRANSPORTATION",
    "LAND TRANSPORTATION OFFICE", "DRIVER'S LICENSE", "DRIVERS LICENSE",
    "LICENSE", "NON-PROFESSIONAL", "PROFESSIONAL", "Last Name", "First Name",
    "Middle Name", "Nationality", "Date of Birth", "Address", "License No",
    "Expiration Date", "EXPIRATION", "ADDRESS"
]

MIN_KEYWORDS_FOR_SUCCESS = 3
MIN_CONFIDENCE_SCORE = 60

# --- NEW/MODIFIED CONSTANTS FOR DATE EXTRACTION ---
# Date pattern to match YYYY/MM/DD or DD/MM/YYYY with different separators
DATE_PATTERN = r'(\d{4}[/.-]\d{2}[/.-]\d{2}|\d{2}[/.-]\d{2}[/.-]\d{4})'
EXPIRATION_KEYWORDS_SEARCH = ["EXPIRATION DATE", "EXPIRATION", "EXP DATE", "DATE OF EXPIRATION"]
# ---------------------------------------------------

@dataclass
class NameInfo:
    document_type: str
    name: str
    document_verified: str
    formatted_text: str
    fingerprint_info: Optional[dict] = None
    match_score: Optional[float] = None
    # === RE-ADDED: Expiration Date ===
    expiration_date: Optional[str] = None
    # =================================

# ============== NETWORK & ONLINE OCR ==============

def _is_online() -> bool:
    """Check for an active internet connection."""
    try:
        # Connect to a known reliable host (Google's DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        print("✅ System is Online. Attempting to use API OCR.")
        return True
    except OSError:
        print("❌ System is Offline. Using local OCR engine.")
        return False

def _extract_text_online(image_path: str) -> Optional[str]:
    """Extracts text using the OCR.space API. (FIXED: Checks for empty text)"""
    try:
        if 'K81234567888957' in OCR_SPACE_API_KEY:
            print("⚠️ WARNING: OCR.space API key is a placeholder. Please update.")
            return None

        with Image.open(image_path) as img:
            # Resize for API compliance and performance
            img.thumbnail((1500, 1500))
            output_buffer = BytesIO()
            img.save(output_buffer, format='JPEG')
            image_bytes = output_buffer.getvalue()

        print(f"Sending image to OCR.space API ({len(image_bytes) / 1024:.1f} KB)...")
        payload = {'apikey': OCR_SPACE_API_KEY, 'language': 'eng', 'scale': 'true', 'OCREngine': 2}
        files = {'file': ('license.jpg', image_bytes, 'image/jpeg')}

        response = requests.post(OCR_SPACE_URL, files=files, data=payload, timeout=10) # Added timeout
        response.raise_for_status()
        result = response.json()

        if result.get('IsErroredOnProcessing'):
            print(f"❌ API Error: {result.get('ErrorMessage')}")
            return None

        raw_text = result['ParsedResults'][0]['ParsedText']
        
        # --- FIX 1: Check for empty text to prevent misleading success/failure logs ---
        if not raw_text.strip():
            print("❌ API OCR successful, but returned EMPTY TEXT. Treating as failure.")
            return None
        # -----------------------------------------------------------------------------

        print("✅ API OCR successful.")
        return raw_text

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Failed: {e}")
        return None
    except Exception as e:
        print(f"❌ An error occurred during online OCR: {e}")
        return None

# ============== CACHING SYSTEM ==============

def _get_cache_key(image_path: str) -> str:
    try:
        with open(image_path, 'rb') as f:
            # Sample more bytes for better uniqueness
            start = f.read(2048)  # Increased from 1024
            f.seek(-2048, 2)
            end = f.read(2048)
            return hashlib.md5(start + end).hexdigest()
    except:
        return hashlib.md5(image_path.encode()).hexdigest()

def _get_cached_result(image_path: str, method: str) -> Optional[str]:
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_key = f"{_get_cache_key(image_path)}_{method}"
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.txt")

        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
    except:
        pass
    return None

def _cache_result(image_path: str, method: str, text: str):
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_key = f"{_get_cache_key(image_path)}_{method}"
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.txt")

        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(text)
        _cleanup_old_cache()
    except:
        pass

def _cleanup_old_cache():
    try:
        cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.txt')]
        if len(cache_files) > MAX_CACHE_FILES:
            cache_files.sort(key=lambda x: os.path.getmtime(os.path.join(CACHE_DIR, x)))
            for old_file in cache_files[:-MAX_CACHE_FILES]:
                os.remove(os.path.join(CACHE_DIR, old_file))
    except:
        pass

# ============== STUDENT PERMIT DETECTION ==============

def _check_student_permit(text: str) -> bool:
    """Check if the text contains Student Permit indicators"""
    text_upper = text.upper()

    # List of restricted terms/phrases that indicate Student Permit
    restricted_terms = [
        "STUDENT PERMIT", "PERMIT NO.", "OR NUMBER", "AMOUNT PAID",
        "ORNUMBER", "AMOUNTPAID"
    ]

    # Check for any restricted terms
    for term in restricted_terms:
        if term in text_upper:
            return True

    # Additional check: if both "STUDENT" and "PERMIT" appear together
    if "STUDENT" in text_upper and "PERMIT" in text_upper:
        return True

    return False

# ============== IMAGE PROCESSING ==============

def _resize_image_optimal(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]

    if (MIN_WIDTH <= w <= OPTIMAL_WIDTH and MIN_HEIGHT <= h <= OPTIMAL_HEIGHT):
        return image

    if w > OPTIMAL_WIDTH or h > OPTIMAL_HEIGHT:
        scale = min(OPTIMAL_WIDTH / w, OPTIMAL_HEIGHT / h)
    else:
        scale = min(MIN_WIDTH / w, MIN_HEIGHT / h)

    new_w, new_h = int(w * scale), int(h * scale)
    interpolation = cv2.INTER_CUBIC if scale > 1 else cv2.INTER_LANCZOS4

    return cv2.resize(image, (new_w, new_h), interpolation=interpolation)

def _preprocess_image(image: np.ndarray, method: str = "standard") -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

    if method == "fast":
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    elif method == "standard":
        # FASTER: Use equalizeHist instead of CLAHE, medianBlur instead of bilateral
        enhanced = cv2.equalizeHist(gray)
        denoised = cv2.medianBlur(enhanced, 3)
        return cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    else:  # detailed
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))  # Reduced complexity
        enhanced = clahe.apply(gray)
        # REMOVE: cv2.fastNlMeansDenoising() - this is the slowest operation!
        kernel = np.ones((1, 1), np.uint8)  # Smaller kernel
        morph = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        return cv2.adaptiveThreshold(morph, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

# ============== OCR PROCESSING (CORE LOGIC) ==============

def _count_verification_keywords(text: str) -> int:
    text_upper = text.upper()
    return sum(1 for keyword in VERIFICATION_KEYWORDS if keyword in text_upper)

def _calculate_confidence_score(text: str, keywords_found: int) -> int:
    base_score = min(90, max(30, (keywords_found / len(VERIFICATION_KEYWORDS)) * 100))

    if len(text.strip()) > 50:
        base_score += 10
    if re.search(r'[A-Z]\d{2}-\d{2}-\d{6}|[A-Z]\d{8}|\d{10}', text):
        base_score += 5
    if re.search(r'\d{2}[-/]\d{2}[-/]\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text):
        base_score += 5

    return min(100, int(base_score))

# --- FIXED FUNCTION TO EXTRACT EXPIRATION DATE (Bug Fix) ---

def _extract_expiration_date(raw_text: str) -> Optional[str]:
    """
    Extracts the expiration date by finding all valid date patterns and selecting
    the one that is not the Date of Birth. It assumes the expiration date is the
    latest (most future) date on the license.
    """
    # This pattern specifically looks for YYYY/MM/DD or YYYY-MM-DD formats
    # The \b ensures we match whole words and don't pick dates from inside other numbers.
    DATE_PATTERN = r'\b(\d{4}[/.-]\d{2}[/.-]\d{2})\b'

    all_dates_found = re.findall(DATE_PATTERN, raw_text)

    if not all_dates_found:
        return None

    valid_dates = []
    for date_str in all_dates_found:
        # Normalize the date format to use '/' for consistency
        normalized_date_str = date_str.replace('-', '/').replace('.', '/')
        
        try:
            # Convert string to a real date object to validate it (e.g., month isn't 13)
            date_obj = datetime.strptime(normalized_date_str, '%Y/%m/%d')

            # Check the context to see if it's the "Date of Birth"
            date_index = raw_text.find(date_str)
            context_before = raw_text[max(0, date_index - 30):date_index].upper()

            # If the text before the date mentions "BIRTH", we skip it.
            if "BIRTH" in context_before or "DOB" in context_before:
                continue
            
            valid_dates.append(date_obj)

        except ValueError:
            # Ignore matches that aren't valid dates (e.g., "2025/15/50")
            continue

    if not valid_dates:
        return None

    # The expiration date is the latest date found on the license.
    latest_date = max(valid_dates)

    return latest_date.strftime('%Y/%m/%d')

# -----------------------------------------------

def _extract_text_smart(image_path: str, is_guest: bool = False, reference_name: str = "") -> str:
    """
    Main OCR function with Online/Offline capability.
    Tries online API first if available, otherwise falls back to local processing.
    """
    # --- Step 1: Attempt Online OCR ---
    if _is_online():
        online_text = _extract_text_online(image_path)
        if online_text:
            # Cache the successful online result
            _cache_result(image_path, "online", online_text)
            return online_text
        else:
            print("⚠️ Online OCR failed. Falling back to local engine.")

    # --- Step 2: Fallback to Offline (Local) OCR ---
    print("⚙️ Using local OCR (Tesseract)...")
    cache_method = "guest_local" if is_guest else "smart_local"
    cached_result = _get_cached_result(image_path, cache_method)
    if cached_result:
        return cached_result

    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")

        image = _resize_image_optimal(image)
        start_time = time.time()

        # OPTIMIZATION: Smarter method selection
        if is_guest:
            methods = [
                ("fast", OCR_CONFIG_FAST),
                ("standard", OCR_CONFIG_STANDARD)
            ]
            min_keywords_needed, min_confidence_needed = 1, 40
        else:
            # For students/staff with reference_name - prioritize speed
            if reference_name:
                methods = [
                    ("fast", OCR_CONFIG_FAST),
                    ("standard", OCR_CONFIG_STANDARD),
                    ("detailed", OCR_CONFIG_DETAILED)  # Only if needed
                ]
            else:
                methods = [
                    ("fast", OCR_CONFIG_FAST),
                    ("standard", OCR_CONFIG_STANDARD),
                    ("detailed", OCR_CONFIG_DETAILED)
                ]
            min_keywords_needed, min_confidence_needed = MIN_KEYWORDS_FOR_SUCCESS, MIN_CONFIDENCE_SCORE

        best_text, best_score = "", 0

        for method_name, ocr_config in methods:
            try:
                processed = _preprocess_image(image, method_name)
                text = pytesseract.image_to_string(processed, config=ocr_config)

                keywords_found = _count_verification_keywords(text)
                confidence = _calculate_confidence_score(text, keywords_found)

                if confidence > best_score:
                    best_score = confidence
                    best_text = text

                # OPTIMIZATION: Early success for students/staff with name matching
                if not is_guest and reference_name and keywords_found >= 2 and confidence >= 60:
                    print(f"⚡ Fast local success for {reference_name}: {keywords_found} keywords")
                    break

                # Standard early exit conditions
                if keywords_found >= min_keywords_needed and confidence >= min_confidence_needed:
                    break

                # Timeout check
                timeout = 4 if is_guest else 5  # Reduced timeouts
                if time.time() - start_time > timeout:
                    break

            except Exception:
                continue

        _cache_result(image_path, cache_method, best_text)
        return best_text

    except Exception as e:
        return f"Error extracting text: {str(e)}"

# ============== TEMP FILE MANAGEMENT ==============

_temp_files = []

def register_temp_file(filepath: str) -> None:
    global _temp_files
    if filepath not in _temp_files:
        _temp_files.append(filepath)

def cleanup_all_temp_files() -> None:
    global _temp_files
    for filepath in _temp_files[:]:
        _safe_delete_temp_file(filepath)

def safe_delete_temp_file(filepath: str) -> None:
    _safe_delete_temp_file(filepath)

def _safe_delete_temp_file(filepath: str) -> None:
    global _temp_files
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            if filepath in _temp_files:
                _temp_files.remove(filepath)
    except:
        pass

atexit.register(cleanup_all_temp_files)

# ============== MAIN OCR FUNCTIONS ==============

def extract_text_from_image(image_path: str, config: str = OCR_CONFIG_STANDARD) -> str:
    text = _extract_text_smart(image_path, is_guest=False)

    # NEW: Check for Student Permit restriction
    if _check_student_permit(text):
        print("❌ Student Permit detected in OCR - Access denied")
        raise ValueError("STUDENT_PERMIT_DETECTED")

    return text

def find_best_line_match(input_name: str, ocr_lines: List[str]) -> Tuple[Optional[str], float]:
    """FIXED: More accurate similarity scoring to prevent false high matches"""
    if not input_name or not ocr_lines:
        return None, 0.0

    best_match, best_score = None, 0.0
    input_name_lower = input_name.lower().strip()

    for line in ocr_lines:
        line_clean = line.strip()
        if not line_clean or len(line_clean) < 3:  # Skip very short lines
            continue

        line_lower = line_clean.lower()

        # EXACT MATCH - highest priority
        if input_name_lower == line_lower:
            return line_clean, 1.0

        # Calculate base similarity using SequenceMatcher
        base_similarity = difflib.SequenceMatcher(None, input_name_lower, line_lower).ratio()

        # WORD-BASED MATCHING - more reliable than character matching
        input_words = set(word.strip() for word in input_name_lower.split() if len(word.strip()) >= 2)
        line_words = set(word.strip() for word in line_lower.split() if len(word.strip()) >= 2)

        if not input_words:  # Handle edge case
            score = base_similarity
        else:
            # FIXED: Calculate word overlap ratio correctly (intersection / reference words)
            word_overlap = len(input_words.intersection(line_words))
            word_overlap_ratio = word_overlap / len(input_words)  # Use reference words as denominator

            # CONSERVATIVE scoring - be stricter
            if word_overlap_ratio >= 0.8:  # 80%+ word overlap
                score = max(0.9, base_similarity)
            elif word_overlap_ratio >= 0.6:  # 60%+ word overlap
                score = max(0.75, base_similarity)
            elif word_overlap_ratio >= 0.4:  # 40%+ word overlap
                score = max(0.6, base_similarity)
            else:
                # Low word overlap - use base similarity but cap it
                score = min(base_similarity, 0.5)  # Cap low overlap matches

        # FIXED: Much more conservative substring matching
        # Only boost if we have significant substring match AND decent base similarity
        if base_similarity >= 0.4:  # Only if there's already reasonable similarity
            if (len(input_name_lower) >= 10 and input_name_lower in line_lower) or \
               (len(line_lower) >= 10 and line_lower in input_name_lower):
                # Only small boost for substring matches, and cap the result
                score = min(score + 0.1, 0.8)  # Cap at 80% for substring matches

        # Update best match if this is better
        if score > best_score:
            best_score = score
            best_match = line_clean

    return best_match, best_score

# In services/license_reader.py

def extract_name_from_lines(ocr_text: str, reference_name: str = "", best_ocr_match: str = "", match_score: float = 0.0) -> Dict[str, str]:
    """
    MODIFIED to accept pre-extracted ocr_text to avoid a redundant API call.
    """
    if not reference_name:
        # This path shouldn't be taken for students, but it's safe to keep
        return extract_guest_name_from_license_simple(ocr_text)

    # NO LONGER MAKES AN API CALL HERE. USES THE PROVIDED TEXT.
    raw_text = ocr_text 
    
    if _check_student_permit(raw_text):
        print("❌ Student Permit detected in license processing - Access denied")
        raise ValueError("STUDENT_PERMIT_DETECTED")

    full_text = " ".join(raw_text.splitlines()).upper()
    keywords_found = _count_verification_keywords(full_text)
    name_matches = False

    if reference_name and match_score >= 0.65:
        name_matches = True
        print(f"🎯 Name match detected ({match_score*100:.1f}%) - License validation override applied")

    if name_matches:
        is_verified = True
        doc_status = "Driver's License Detected (Name Match Override)"
    else:
        is_verified = keywords_found >= 1
        doc_status = "Driver's License Detected" if is_verified else "Unverified Document"

    name_info = {"Document Verified": doc_status}

    if reference_name and match_score >= 0.65:
        name_info.update({
            "Name": reference_name,
            "Matched From": "Fingerprint Authentication (High Confidence)",
            "Match Confidence": f"{match_score * 100:.1f}%"
        })
    elif best_ocr_match and match_score > 0.50:
        name_info.update({
            "Name": best_ocr_match,
            "Matched From": "Best OCR Line Match",
            "Match Confidence": f"{match_score * 100:.1f}%"
        })
    else:
        detected_name = _detect_name_pattern(raw_text)
        if detected_name:
            name_info.update({"Name": detected_name, "Matched From": "Pattern Detection"})
        else:
            name_info["Name"] = "Not Found"
            if reference_name:
                name_info["Name"] = reference_name

    return name_info

def extract_guest_name_from_license_simple(image_path: str) -> Dict[str, str]:
    raw_text = _extract_text_smart(image_path, is_guest=True)

    # NEW: Check for Student Permit restriction for guests
    if _check_student_permit(raw_text):
        print("❌ Student Permit detected in guest license processing - Access denied")
        raise ValueError("STUDENT_PERMIT_DETECTED")

    full_text = " ".join(raw_text.splitlines()).upper()

    keywords_found = _count_verification_keywords(full_text)
    is_verified = keywords_found >= 1

    doc_status = "Driver's License Detected" if is_verified else "Document Detected"
    ocr_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    detected_name = extract_guest_name_from_license(ocr_lines)

    return {
        "Document Verified": doc_status,
        "Name": detected_name if detected_name and detected_name != "Guest" else "Guest User",
        "Matched From": "Simple Guest Extraction" if detected_name and detected_name != "Guest" else "Default Guest Name"
    }

def extract_guest_name_from_license(ocr_lines: List[str]) -> str:
    # Enhanced filter keywords
    filter_keywords = [
        'REPUBLIC', 'PHILIPPINES', 'DEPARTMENT', 'TRANSPORTATION',
        'LAND TRANSPORTATION OFFICE', 'DRIVER', 'LICENSE', 'DRIVERS LICENSE',
        'NON-PROFESSIONAL', 'PROFESSIONAL', 'NATIONALITY', 'ADDRESS',
        'DATE OF BIRTH', 'EXPIRATION', 'AGENCY CODE', 'CONDITIONS',
        'EYES COLOR', 'WEIGHT', 'HEIGHT', 'BLOOD TYPE', 'RESTRICTION',
        'SIGNATURE', 'PHOTO', 'FIRST NAME', 'LAST NAME', 'MIDDLE NAME',
        'CITY', 'PROVINCE', 'BARANGAY', 'STREET', 'ROAD', 'AVENUE',
        'RESIDENCIA', 'BLK', 'LOT',
        'LN', 'FNMN', 'LNFMMH', 'LNFN,MN', 'LN, FNMN', 'MN', 'Agency Code', 'Code', 'DL Codes',
        'Ln,Fnmn'
    ]

    # Stop markers specific to Philippine licenses
    stop_markers = [
        'NATIONALITY', 'SEX', 'DATE OF BIRTH', 'WEIGHT', 'HEIGHT',
        'ADDRESS', 'LICENSE NO', 'EXPIRATION DATE', 'AGENCY CODE',
        'BLOOD TYPE', 'EYES COLOR', 'DL CODES', 'CONDITIONS',
        'PHL', 'BLK', 'LOT', 'RESIDENCIA', 'SIGNATURE',
        'M', 'F', 'BROWN', 'BLACK', 'BLUE', 'NONE',
        'EN', 'ED', 'AC', 'YC', 'DLC', 'SI', 'S'
    ]

    name_markers = ['LNFMMH', 'LNFMM', 'LN FN MN', 'LAST NAME', 'FIRST NAME', 'LNFN, MN', 'LNFN,MN', 'Ln,Fnmn'
    ]

    potential_names = []
    name_marker_index = -1

    # Helper function to clean name parts (remove dots and other unwanted characters)
    def clean_name_part(name_part):
        # Remove dots, extra spaces, and keep only letters and spaces
        cleaned = re.sub(r'[^A-Z\s]', '', name_part.strip().upper())
        return cleaned.strip()

    # First pass: find name markers (handle variations with dots/commas)
    for i, line in enumerate(ocr_lines):
        line_clean = line.strip().upper()
        line_normalized = line_clean.replace(' ', '').replace('.', '').replace(',', '')
        for marker in name_markers:
            marker_normalized = marker.replace(' ', '').replace('.', '').replace(',', '')
            if marker_normalized in line_normalized:
                name_marker_index = i
                break
        if name_marker_index >= 0:
            break

    # Second pass: extract names with stop marker awareness
    for i, line in enumerate(ocr_lines):
        line_clean = line.strip().upper()

        # If we found a name marker, prioritize the next line
        if name_marker_index >= 0 and i == name_marker_index + 1:
            if not any(char.isdigit() for char in line_clean) and len(line_clean) >= 5:
                # Check if it's not a stop marker
                if not any(marker in line_clean or line_clean == marker for marker in stop_markers):
                    # Require exactly one comma for Philippine license format
                    if line_clean.count(',') == 1:
                        parts = line_clean.split(',')
                        lastname = clean_name_part(parts[0])  # Remove dots here!
                        firstname = clean_name_part(parts[1])  # Remove dots here!

                        if (lastname.replace(' ', '').isalpha() and
                            firstname.replace(' ', '').isalpha() and
                            len(lastname) >= 2 and len(firstname) >= 2 and
                            len(lastname) <= 20 and len(firstname) <= 30):
                            # Reconstruct the clean name
                            clean_line = f"{lastname}, {firstname}"
                            score = 100  # Highest score for lines after name markers
                            potential_names.append((clean_line, score))
                            # Don't continue looking past the name field
                            break

        # Skip lines after we've passed the name field (if we found a marker)
        if name_marker_index >= 0 and i > name_marker_index + 2:
            # Check if we're now in other fields
            if any(marker in line_clean for marker in stop_markers):
                break

        if (not line_clean or len(line_clean) < 5 or len(line_clean) > 50 or
            any(char.isdigit() for char in line_clean)):
            continue

        # Skip lines that ARE keywords or stop markers
        if line_clean in filter_keywords or line_clean in stop_markers:
            continue

        # Skip lines that start with keywords
        skip_line = False
        for keyword in filter_keywords + stop_markers:
            if line_clean.startswith(keyword + ' '):
                skip_line = True
                break

        if skip_line:
            continue

        # STRICT: Require exactly one comma
        comma_count = line_clean.count(',')
        if comma_count != 1:
            continue

        # Score potential names
        score = 0

        # Philippine license format: exactly one comma (LASTNAME,FIRSTNAME)
        parts = line_clean.split(',')
        lastname = clean_name_part(parts[0])  # Remove dots here too!
        firstname = clean_name_part(parts[1])  # Remove dots here too!

        if (lastname.replace(' ', '').isalpha() and
            firstname.replace(' ', '').isalpha() and
            len(lastname) >= 2 and len(firstname) >= 2 and
            len(lastname) <= 20 and len(firstname) <= 30):
            # Check it's not an address
            clean_line = f"{lastname}, {firstname}"
            if not any(addr_marker in clean_line for addr_marker in ['BLK', 'LOT', 'PH', 'PHASE']):
                score += 20  # Base score for proper format

                # Length scoring
                if 10 <= len(clean_line) <= 30:
                    score += 3

                # Proximity to name marker
                if name_marker_index >= 0:
                    distance = abs(i - name_marker_index - 1)
                    if distance == 0:
                        score += 50  # Right after marker
                    elif distance == 1:
                        score += 20  # One line away
                    elif distance > 3:
                        score -= 10  # Too far from marker

                if score > 0:
                    potential_names.append((clean_line, score))

    if potential_names:
        potential_names.sort(key=lambda x: x[1], reverse=True)
        best_name = potential_names[0][0]
        return _format_extracted_name_simple(best_name)

    return "Guest"

def _format_extracted_name_simple(name: str) -> str:
    """
    Format the extracted name as ALL CAPITAL LETTERS in SURNAME, FIRSTNAME MIDDLENAME format
    """
    if ',' in name:
        parts = name.split(',')
        if len(parts) == 3:
            surname = parts[0].strip().upper()
            firstname = parts[1].strip().upper()

            return f"{surname}, {firstname}"

        elif len(parts) == 2:
            # Handle 2-part format: SURNAME, FIRSTNAME MIDDLENAME
            surname = parts[0].strip().upper()
            firstname_part = parts[1].strip().upper()

            # Check if there's a space in firstname_part (indicating middle name)
            if ' ' in firstname_part:
                name_parts = firstname_part.split(' ', 1)  # Split only on first space
                firstname = name_parts[0].strip()
                middlename = name_parts[1].strip()

                return f"{surname}, {firstname}, {middlename}"
            else:
                # No middle name, just firstname
                return f"{surname}, {firstname_part}"

    return name.upper()

def _detect_name_pattern(raw_text: str) -> Optional[str]:
    """
    Detects a name in the format 'SURNAME, FIRSTNAME [MIDDLENAME]' from OCR text.
    This pattern is more robust for Philippine Driver's Licenses.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    potential_name = None
    name_marker_found_at = -1

    # --- Pass 1: Look for the line right after a name marker (high confidence) ---
    name_markers = ['LAST NAME', 'FIRST NAME', 'MIDDLE NAME', 'LN', 'FN', 'MN']
    for i, line in enumerate(lines):
        line_upper = line.upper()
        # A good marker line contains at least two of the name-related keywords
        if sum(1 for marker in name_markers if marker in line_upper) >= 2:
            name_marker_found_at = i
            # The next line is the most likely candidate for the name
            if i + 1 < len(lines):
                candidate_line = lines[i + 1].strip().upper()
                # A valid name must have one comma and no digits.
                if candidate_line.count(',') == 1 and not any(char.isdigit() for char in candidate_line):
                    parts = [p.strip() for p in candidate_line.split(',')]
                    # Ensure both surname and given name parts are valid
                    if len(parts) == 2 and parts[0] and parts[1]:
                        # This is a high-confidence match, return it immediately.
                        return candidate_line
            break # Stop after finding the first valid marker line

    # --- Pass 2: Fallback if no marker was found, search all lines for the pattern ---
    for i, line in enumerate(lines):
        # Skip the marker line itself to avoid matching it as a name
        if i == name_marker_found_at:
            continue

        # Rule: Must have exactly one comma, no digits, and be a reasonable length.
        if line.count(',') != 1 or any(char.isdigit() for char in line) or not (5 < len(line) < 50):
            continue

        parts = [p.strip() for p in line.split(',')]
        if len(parts) == 2 and parts[0] and parts[1]:
            surname = parts[0]
            given_names = parts[1]

            # Rule: Both parts must contain only letters and spaces.
            is_surname_valid = all(c.isalpha() or c.isspace() for c in surname)
            is_given_name_valid = all(c.isalpha() or c.isspace() for c in given_names)

            if is_surname_valid and is_given_name_valid:
                # Rule: Avoid lines that look like addresses.
                line_upper = line.upper()
                address_keywords = ['BLK', 'LOT', 'STREET', 'AVE', 'ROAD', 'BRGY', 'CITY']
                if not any(keyword in line_upper for keyword in address_keywords):
                    # This is our best guess.
                    return line.upper()

    return None # Return None if no suitable name is found

def package_name_info(structured_data: Dict[str, str], basic_text: str, 
                      fingerprint_info: Optional[dict] = None,
                      expiration_date: Optional[str] = None) -> NameInfo:
    return NameInfo(
        document_type="Driver's License",
        name=structured_data.get('Name', 'Not Found'),
        document_verified=structured_data.get('Document Verified', 'Unverified'),
        formatted_text=basic_text,
        fingerprint_info=fingerprint_info,
        expiration_date=expiration_date
    )

# ============== CAMERA FUNCTIONS ==============

def auto_capture_license_rpi(reference_name: str = "", fingerprint_info: Optional[dict] = None, retry_mode: bool = False) -> Optional[str]:
    """
    Auto-capture license using RPi Camera with ROI-only enhancement and stability tracking

    Returns:
        tuple: (image_path, reason) where reason is:
            - "success": Capture successful
            - "cancelled": User cancelled (pressed 'q' or cancel button)
            - "student_permit": Student permit detected in preview
            - "camera_error": Camera initialization failed
    """
    camera = get_camera()
    if not camera.initialized:
        return (None, "camera_error")

    set_led_white_lighting()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"motorpass_license_{fingerprint_info.get('student_id', 'guest')}_{timestamp}" if fingerprint_info else f"motorpass_license_{timestamp}"

    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', prefix=prefix, delete=False)
    temp_filename = temp_file.name
    temp_file.close()
    register_temp_file(temp_filename)

    SCREEN_WIDTH, SCREEN_HEIGHT = 720, 600
    BOX_WIDTH, BOX_HEIGHT = 600, 350
    CAPTURE_DELAY = 1.0
    KEYWORD_CHECK_INTERVAL = 5

    # Stability settings for longer green time
    STABILITY_FRAMES = 1  # Need 1 good reading to go green (reduced from 5 for faster response)
    MIN_GREEN_TIME = 2  # Stay green for at least 2 seconds
    KEYWORD_HISTORY_SIZE = 8  # Track last 8 readings

    frame_count = 0
    captured_frame = None
    ready_time = None
    current_keywords = 0
    keyword_history = []
    good_readings_count = 0
    green_start_time = None

    window_name = "MotorPass - License Capture"
    create_clean_camera_window(window_name, SCREEN_WIDTH, SCREEN_HEIGHT)
    cv2.setMouseCallback(window_name, camera_mouse_callback)
    reset_cancel_state()

    def _enhance_roi_only(roi, keyword_count):
        """Enhance only the ROI based on keyword detection"""
        if keyword_count == 0:
            # Strong enhancement for poor detection
            alpha, beta = 2.0, 50
        elif keyword_count == 1:
            # Medium enhancement
            alpha, beta = 1.6, 35
        elif keyword_count == 2:
            # Light enhancement
            alpha, beta = 1.3, 25
        else:
            # Normal processing
            alpha, beta = 1.1, 15

        enhanced_roi = cv2.convertScaleAbs(roi, alpha=alpha, beta=beta)

        # Additional processing for very poor detection
        if keyword_count < 2:
            gray = cv2.cvtColor(enhanced_roi, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced_gray = clahe.apply(gray)
            enhanced_roi = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)

        return enhanced_roi, alpha

    def _get_adaptive_threshold(keyword_count, keyword_history, is_currently_green):
        """Stable adaptive threshold with hysteresis"""
        if not keyword_history:
            return 3 if keyword_count == 0 else 2

        # Calculate average and stability
        avg_keywords = sum(keyword_history) / len(keyword_history)
        recent_stable = len([k for k in keyword_history[-3:] if k >= 2]) >= 2

        if is_currently_green:
            # Hysteresis: Once green, easier to stay green
            return 1 if recent_stable else 2
        else:
            # Need more evidence to go green
            if avg_keywords >= 2.5 and recent_stable:
                return 2
            elif avg_keywords >= 1.5:
                return 2
            else:
                return 3

    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                break

            original_h, original_w = frame.shape[:2]
            scale = min(SCREEN_WIDTH / original_w, SCREEN_HEIGHT / original_h)
            new_w, new_h = int(original_w * scale), int(original_h * scale)

            # Keep display frame normal - no global brightness changes
            brightened = cv2.convertScaleAbs(frame, alpha=1.2, beta=20)
            mirrored = cv2.flip(brightened, 1)
            display_frame = cv2.resize(mirrored, (new_w, new_h))

            center_x, center_y = new_w // 2, new_h // 2
            box_x1 = max(0, center_x - BOX_WIDTH // 2)
            box_y1 = max(0, center_y - BOX_HEIGHT // 2)
            box_x2 = min(new_w, center_x + BOX_WIDTH // 2)
            box_y2 = min(new_h, center_y + BOX_HEIGHT // 2)

            frame_count += 1
            roi_enhancement_level = 1.0  # Track current ROI enhancement

            # Check for license keywords with stability tracking
            if frame_count % KEYWORD_CHECK_INTERVAL == 0:
                try:
                    orig_box_x1, orig_box_y1 = int(box_x1 / scale), int(box_y1 / scale)
                    orig_box_x2, orig_box_y2 = int(box_x2 / scale), int(box_y2 / scale)

                    # Extract ROI from original brightened frame
                    roi = brightened[orig_box_y1:orig_box_y2, orig_box_x1:orig_box_x2]

                    if roi.size > 0:
                        # Enhance only the ROI based on previous detection
                        enhanced_roi, roi_enhancement_level = _enhance_roi_only(roi, current_keywords)

                        # Perform OCR on enhanced ROI
                        gray_roi = cv2.cvtColor(enhanced_roi, cv2.COLOR_BGR2GRAY)
                        thresh_roi = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                        quick_text = pytesseract.image_to_string(thresh_roi, config=OCR_CONFIG_FAST).upper()

                        # NEW: Check for Student Permit in camera preview
                        if _check_student_permit(quick_text):
                            print("❌ Student Permit detected in camera preview - Stopping capture")
                            cv2.destroyAllWindows()
                            safe_delete_temp_file(temp_filename)
                            return (None, "student_permit")

                        current_keywords = sum(1 for keyword in VERIFICATION_KEYWORDS if keyword in quick_text)

                        # Update keyword history for stability
                        keyword_history.append(current_keywords)
                        if len(keyword_history) > KEYWORD_HISTORY_SIZE:
                            keyword_history.pop(0)

                        # Check if currently in green state
                        is_currently_green = ready_time is not None
                        keywords_needed = _get_adaptive_threshold(current_keywords, keyword_history, is_currently_green)

                        # Stability logic for going green
                        if current_keywords >= keywords_needed:
                            good_readings_count += 1

                            # First time going green - need stable readings
                            if not is_currently_green and good_readings_count >= STABILITY_FRAMES:
                                ready_time = time.time()
                                green_start_time = time.time()
                                good_readings_count = 0  # Reset counter
                            # Already green - stay green with hysteresis
                            elif is_currently_green:
                                pass  # Keep ready_time as is
                        else:
                            good_readings_count = 0

                            # Only lose green state if enough time has passed
                            if is_currently_green and green_start_time:
                                time_green = time.time() - green_start_time
                                if time_green >= MIN_GREEN_TIME:
                                    ready_time = None
                                    green_start_time = None
                            elif not is_currently_green:
                                ready_time = None
                                green_start_time = None
                    else:
                        current_keywords = 0
                        good_readings_count = 0
                        ready_time = None
                        green_start_time = None
                        roi_enhancement_level = 1.0

                except Exception:
                    current_keywords = 0
                    good_readings_count = 0
                    ready_time = None
                    green_start_time = None
                    roi_enhancement_level = 1.0

            is_currently_green = ready_time is not None
            keywords_needed = _get_adaptive_threshold(current_keywords, keyword_history, is_currently_green)
            ready_to_capture = ready_time is not None

            # Show stability progress
            stability_progress = min(100, (good_readings_count / STABILITY_FRAMES) * 100)
            green_time = (time.time() - green_start_time) if green_start_time else 0

            # Auto capture after delay - enhance the captured frame based on final ROI enhancement
            if ready_to_capture and (time.time() - ready_time) >= CAPTURE_DELAY:
                # Apply the same enhancement level to the full frame for capture
                if roi_enhancement_level > 1.2:
                    captured_frame = cv2.convertScaleAbs(frame, alpha=roi_enhancement_level, beta=30)
                else:
                    captured_frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=20)
                break

            # Determine colors and status with stability info
            enhancement_info = f" (ROI: {roi_enhancement_level:.1f}x)" if roi_enhancement_level > 1.0 else ""

            if ready_to_capture:
                box_color = (0, 255, 0)
                remaining_delay = CAPTURE_DELAY - (time.time() - ready_time) if ready_time else CAPTURE_DELAY
                green_duration = f" [Green: {green_time:.1f}s]" if green_time > 0 else ""
                status_text = f"READY! Capturing in {remaining_delay:.1f}s... ({current_keywords}/{keywords_needed}){enhancement_info}{green_duration}"
                status_color = (0, 255, 0)
            elif good_readings_count > 0:
                box_color = (0, 255, 255)
                progress_text = f" [Stabilizing: {good_readings_count}/{STABILITY_FRAMES}]"
                status_text = f"Stabilizing... Found {current_keywords}/{keywords_needed} keywords{enhancement_info}{progress_text}"
                status_color = (0, 255, 255)
            elif current_keywords >= max(1, keywords_needed - 1):
                box_color = (0, 255, 255)
                avg_text = f" [Avg: {sum(keyword_history)/len(keyword_history):.1f}]" if keyword_history else ""
                status_text = f"Almost ready... Found {current_keywords}/{keywords_needed} keywords{enhancement_info}{avg_text}"
                status_color = (0, 255, 255)
            elif current_keywords >= 1:
                box_color = (0, 165, 255)
                status_text = f"License detected! Found {current_keywords}/{keywords_needed} keywords{enhancement_info}"
                status_color = (0, 165, 255)
            else:
                box_color = (0, 0, 255)
                status_text = f"Position license in box... ({current_keywords} keywords){enhancement_info}"
                status_color = (255, 255, 255)

            # Draw UI elements with ROI enhancement visualization
            # Make box color intensity reflect ROI enhancement level
            if roi_enhancement_level > 1.5:
                box_thickness = 4  # Thicker box for high enhancement
            else:
                box_thickness = 3

            cv2.rectangle(display_frame, (box_x1, box_y1), (box_x2, box_y2), box_color, box_thickness)

            # Optional: Show enhanced ROI preview in corner when enhancement is active
            if roi_enhancement_level > 1.2 and frame_count % KEYWORD_CHECK_INTERVAL == 0:
                try:
                    orig_box_x1, orig_box_y1 = int(box_x1 / scale), int(box_y1 / scale)
                    orig_box_x2, orig_box_y2 = int(box_x2 / scale), int(box_y2 / scale)
                    roi_preview = brightened[orig_box_y1:orig_box_y2, orig_box_x1:orig_box_x2]
                    enhanced_preview, _ = _enhance_roi_only(roi_preview, current_keywords)

                    # Resize preview and place in corner
                    preview_h, preview_w = enhanced_preview.shape[:2]
                    preview_scale = min(150 / preview_w, 100 / preview_h)
                    preview_resized = cv2.resize(enhanced_preview, (int(preview_w * preview_scale), int(preview_h * preview_scale)))

                    # Place in top-right corner
                    y1, y2 = 10, 10 + preview_resized.shape[0]
                    x1, x2 = new_w - preview_resized.shape[1] - 10, new_w - 10

                    if y2 < new_h and x1 > 0:
                        display_frame[y1:y2, x1:x2] = preview_resized
                        cv2.rectangle(display_frame, (x1-1, y1-1), (x2+1, y2+1), (0, 255, 255), 1)
                        cv2.putText(display_frame, "Enhanced", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)
                except:
                    pass

            camera_status = "RETAKE MODE" if retry_mode else "License Capture [ROI Focus]"
            cv2.putText(display_frame, camera_status, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255) if retry_mode else (0, 255, 0), 2)

            if reference_name:
                cv2.putText(display_frame, f"Target: {reference_name}", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.putText(display_frame, status_text, (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
            cv2.putText(display_frame, "Auto-capture | 's' = manual | 'q' = quit", (10, new_h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

            # Progress bar with stability and ROI enhancement indicator
            if current_keywords >= 0:
                # Show stability progress if working towards green
                if good_readings_count > 0 and not ready_to_capture:
                    progress_width = int((good_readings_count / STABILITY_FRAMES) * 200)
                    progress_color = (0, 255, 255)  # Cyan for stability progress
                    progress_text = f"Stabilizing: {good_readings_count}/{STABILITY_FRAMES} | ROI: {roi_enhancement_level:.1f}x"
                else:
                    # Normal keyword progress
                    progress_width = int((current_keywords / max(keywords_needed, 1)) * 200)

                    # Color based on enhancement level and state
                    if ready_to_capture:
                        progress_color = (0, 255, 0)  # Green when ready
                    elif roi_enhancement_level >= 1.8:
                        progress_color = (0, 100, 255)  # Orange for high enhancement
                    elif roi_enhancement_level >= 1.4:
                        progress_color = (0, 200, 255)  # Yellow for medium enhancement
                    else:
                        progress_color = box_color

                    if ready_to_capture:
                        progress_text = f"READY! Keywords: {current_keywords}/{keywords_needed} | Green Time: {green_time:.1f}s"
                    else:
                        avg_text = f" | Avg: {sum(keyword_history)/len(keyword_history):.1f}" if keyword_history else ""
                        progress_text = f"Keywords: {current_keywords}/{keywords_needed} | ROI: {roi_enhancement_level:.1f}x{avg_text}"

                cv2.rectangle(display_frame, (10, new_h-40), (210, new_h-25), (50, 50, 50), -1)
                cv2.rectangle(display_frame, (10, new_h-40), (10 + progress_width, new_h-25), progress_color, -1)
                cv2.putText(display_frame, progress_text, (10, new_h-45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Countdown
            if ready_to_capture and ready_time:
                remaining = CAPTURE_DELAY - (time.time() - ready_time)
                if remaining > 0:
                    countdown_text = f"{remaining:.1f}"
                    text_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
                    text_x = (new_w - text_size[0]) // 2
                    text_y = (new_h + text_size[1]) // 2
                    cv2.putText(display_frame, countdown_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

            frame_with_button, _ = add_cancel_button_overlay(display_frame)
            cv2.imshow(window_name, frame_with_button)

            if is_cancel_clicked():
                print("❌ License capture cancelled")
                break

            key = cv2.waitKey(30) & 0xFF
            if key == ord("q"):
                print("\n🛑 License capture cancelled by user")
                break
            elif key == ord("s"):
                # Manual capture with current enhancement level
                if roi_enhancement_level > 1.2:
                    captured_.frame = cv2.convertScaleAbs(frame, alpha=roi_enhancement_level, beta=30)
                else:
                    captured_frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=20)
                break

        cv2.destroyAllWindows()

        if captured_frame is not None:
            optimized_frame = _resize_image_optimal(captured_frame)
            cv2.imwrite(temp_filename, optimized_frame)
            return (temp_filename, "success")
        else:
            safe_delete_temp_file(temp_filename)
            return (None, "cancelled")

    except Exception:
        cv2.destroyAllWindows()
        safe_delete_temp_file(temp_filename)
        return (None, "camera_error")

# ============== VERIFICATION FUNCTIONS ==============

def licenseRead(image_path: str, fingerprint_info: dict) -> NameInfo:
    """
    MODIFIED to perform OCR only ONCE and pass the text to other functions.
    """
    reference_name = fingerprint_info['name']

    try:
        # =================== THE FIX: OCR ONCE ===================
        # This is now the ONLY OCR call in this entire flow.
        try:
            basic_text = extract_text_from_image(image_path)
        except ValueError as e:
            # Handle student permit detection directly
            if "STUDENT_PERMIT_DETECTED" in str(e):
                error_packaged = package_name_info(
                    {"Name": "STUDENT PERMIT DETECTED", "Document Verified": "DENIED - Student Permit Not Allowed"},
                    "Student Permit detected - Access denied", fingerprint_info, expiration_date=None
                )
                error_packaged.match_score = 0.0
                return error_packaged
            else:
                raise e
        # =========================================================

        extracted_date = _extract_expiration_date(basic_text)
        print(f"📅 Extracted Expiration Date: {extracted_date or 'Not Found'}")
        
        detected_name = _detect_name_pattern(basic_text)

        # Calculate similarity score
        import difflib
        normalized_detected_raw = detected_name.lower().strip().replace('\xa0', '').replace(' ', '').replace(',', '') if detected_name else ""
        normalized_reference_raw = reference_name.lower().strip().replace('\xa0', '').replace(' ', '').replace(',', '') if reference_name else ""
        
        if normalized_detected_raw and normalized_reference_raw:
            sim_score = difflib.SequenceMatcher(None, normalized_detected_raw, normalized_reference_raw).ratio()
        else:
            sim_score = difflib.SequenceMatcher(None, basic_text.lower().replace('\xa0', ' ').replace('\n', ' '), reference_name.lower().strip().replace('\xa0', ' ')).ratio()

        # Pass the basic_text we already have, NOT the image_path
        structured_data = extract_name_from_lines(basic_text, reference_name, detected_name, sim_score)

        # Package the result
        packaged = package_name_info(structured_data, basic_text, fingerprint_info, expiration_date=extracted_date)
        packaged.match_score = sim_score
        
        if packaged.name == "Not Found" and reference_name:
             packaged.name = reference_name

        return packaged

    except Exception as e:
        print(f"❌ Error in licenseRead: {e}")
        error_packaged = package_name_info(
            {"Name": "Not Found", "Document Verified": "Failed"},
            "Processing failed", fingerprint_info, expiration_date=None
        )
        error_packaged.match_score = 0.0
        return error_packaged
    finally:
        safe_delete_temp_file(image_path)

def licenseReadGuest(image_path: str, guest_info: dict) -> NameInfo:
    """Simplified guest license reading - auto-accepts results without retake prompts"""
    reference_name = guest_info['name']  # Use guest name as reference

    try:
        # Extract text from image
        try:
            basic_text = extract_text_from_image(image_path)
        except ValueError as e:
            if "STUDENT_PERMIT_DETECTED" in str(e):
                # Return error result for Student Permit
                guest_fingerprint_info = {
                    'name': reference_name,
                    'confidence': 100,
                    'user_type': 'GUEST'
                }
                error_packaged = package_name_info(
                    {"Name": "STUDENT PERMIT DETECTED", "Document Verified": "DENIED - Student Permit Not Allowed"},
                    "Student Permit detected - Access denied", guest_fingerprint_info, expiration_date=None
                )
                error_packaged.match_score = 0.0
                return error_packaged
            else:
                raise e
        
        # Extract expiration date
        extracted_date = _extract_expiration_date(basic_text)
        print(f"📅 Guest Extracted Expiration Date: {extracted_date or 'Not Found'}")

        # Extract OCR lines and use find_best_line_match for consistency
        ocr_lines = [line.strip() for line in basic_text.splitlines() if line.strip()]
        name_from_ocr, sim_score = find_best_line_match(reference_name, ocr_lines)

        # Use the same enhanced verification as student/staff
        try:
            structured_data = extract_name_from_lines(image_path, reference_name, name_from_ocr, sim_score)
        except ValueError as e:
            if "STUDENT_PERMIT_DETECTED" in str(e):
                # Return error result for Student Permit
                guest_fingerprint_info = {
                    'name': reference_name,
                    'confidence': 100,
                    'user_type': 'GUEST'
                }
                error_packaged = package_name_info(
                    {"Name": "STUDENT PERMIT DETECTED", "Document Verified": "DENIED - Student Permit Not Allowed"},
                    "Student Permit detected - Access denied", guest_fingerprint_info, expiration_date=None
                )
                error_packaged.match_score = 0.0
                return error_packaged
            else:
                raise e

        # Create guest-specific fingerprint_info for compatibility
        guest_fingerprint_info = {
            'name': reference_name,
            'confidence': 100,  # High confidence since it's user-provided
            'user_type': 'GUEST'
        }

        # Package the result
        packaged = package_name_info(structured_data, basic_text, guest_fingerprint_info, expiration_date=extracted_date)
        packaged.match_score = sim_score

        # SIMPLIFIED: Auto-accept all guest results - no retake prompts
        print(f"✅ Guest license processed: Auto-accepting scan result")
        return packaged

    except Exception as e:
        print(f"❌ Error in guest license processing: {e}")
        guest_fingerprint_info = {
            'name': reference_name,
            'confidence': 100,
            'user_type': 'GUEST'
        }
        error_packaged = package_name_info(
            {"Name": "Processing Error", "Document Verified": "Failed"},
            "Processing failed", guest_fingerprint_info, expiration_date=None
        )
            
        error_packaged.match_score = 0.0
        return error_packaged
    finally:
        # Clean up the image file
        safe_delete_temp_file(image_path)

def get_guest_name_from_license_image(image_path: str) -> str:
    try:
        extraction = extract_guest_name_from_license_simple(image_path)
        detected_name = extraction.get('Name', 'Guest')
        return detected_name if detected_name and detected_name != "Guest User" else "Guest"
    except ValueError as e:
        if "STUDENT_PERMIT_DETECTED" in str(e):
            return "STUDENT_PERMIT_DETECTED"
        return "Guest"
    except Exception:
        return "Guest"


# ============== VERIFICATION FLOWS ==============

def complete_verification_flow(image_path: str, fingerprint_info: dict,
                             helmet_verified: bool = True,
                             license_expiration_valid: bool = True) -> bool:
    try:
        license_result = licenseRead(image_path, fingerprint_info)
    except ValueError as e:
        if "STUDENT_PERMIT_DETECTED" in str(e):
            print("❌ Student Permit detected - Verification FAILED")
            return False
        else:
            raise e

    # Check if Student Permit was detected
    if license_result.name == "STUDENT PERMIT DETECTED":
        print("❌ Student Permit detected - Verification FAILED")
        return False

    final_name = license_result.name
    final_match_score = license_result.match_score or 0.0
    final_document_status = license_result.document_verified

    fingerprint_verified = fingerprint_info['confidence'] > 50

    # Check if license is detected (including name match override)
    license_detected = ("Driver's License Detected" in final_document_status or
                       "Name Match Override" in final_document_status)

    name_matching_verified = final_match_score > 0.65

    # If names match, force license detection to be true
    if name_matching_verified:
        license_detected = True
        print(f"🎯 Name match override: License detection forced to TRUE")

    all_verified = (helmet_verified and fingerprint_verified and
                   license_expiration_valid and license_detected and
                   name_matching_verified)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 VERIFICATION RESULTS")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🪖 Helmet: {'✅' if helmet_verified else '❌'}")
    print(f"🔒 Fingerprint: {'✅' if fingerprint_verified else '❌'} ({fingerprint_info['confidence']}%)")
    print(f"📅 License Valid: {'✅' if license_expiration_valid else '❌'}")
    print(f"📅 Expiration Date: {license_result.expiration_date or 'Not Found'}")
    print(f"🆔 License Detected: {'✅' if license_detected else '❌'}" +
          (" (Name Match Override)" if name_matching_verified and license_detected else ""))
    print(f"👤 Name Match: {'✅' if name_matching_verified else '❌'} ({final_match_score*100:.1f}%)")
    print(f"🟢 STATUS: {'✅ FULLY VERIFIED' if all_verified else '❌ VERIFICATION FAILED'}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return all_verified

def complete_guest_verification_flow(image_path: str, guest_info: dict,
                                   helmet_verified: bool = True) -> bool:
    try:
        license_result = licenseReadGuest(image_path, guest_info)
    except ValueError as e:
        if "STUDENT_PERMIT_DETECTED" in str(e):
            print("❌ Student Permit detected - Guest verification FAILED")
            return False
        else:
            raise e

    # Check if Student Permit was detected
    if license_result.name == "STUDENT PERMIT DETECTED":
        print("❌ Student Permit detected - Guest verification FAILED")
        return False

    final_name = license_result.name
    final_match_score = license_result.match_score or 0.0
    final_document_status = license_result.document_verified

    # Check if license is detected (including name match override)
    license_detected = ("Driver's License Detected" in final_document_status or
                       "Name Match Override" in final_document_status)

    name_matching_verified = final_match_score > 0.85

    # If names match, force license detection to be true (same as student/staff)
    if name_matching_verified:
        license_detected = True
        print(f"🎯 Guest name match override: License detection forced to TRUE")

    guest_verified = helmet_verified and license_detected

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 GUEST VERIFICATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🪖 Helmet: {'✅' if helmet_verified else '❌'}")
    print(f"📅 Expiration Date: {license_result.expiration_date or 'Not Found'}")
    print(f"🆔 License Detected: {'✅' if license_detected else '❌'}" +
          (" (Name Match Override)" if name_matching_verified and license_detected else ""))
    print(f"👤 Name Match: {'✅' if name_matching_verified else '❌'} ({final_match_score*100:.1f}%)")
    print(f"🟢 STATUS: {'✅ GUEST VERIFIED' if guest_verified else '❌ GUEST VERIFICATION FAILED'}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return guest_verified
    
def verify_guest_license_from_text(ocr_text: str, guest_info: dict, helmet_verified: bool = True) -> bool:
    """
    Efficiently verifies a guest license using pre-extracted OCR text.
    This avoids making redundant API calls.
    """
    print("\nVerifying guest license from existing OCR text...")
    
    # 1. Extract Expiration Date from the text
    extracted_date = _extract_expiration_date(ocr_text)
    
    # 2. Find the best name match in the text
    ocr_lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
    name_from_ocr, sim_score = find_best_line_match(guest_info['name'], ocr_lines)

    # 3. Determine if the document is a license based on keywords
    keywords_found = _count_verification_keywords(ocr_text)
    doc_status = "Driver's License Detected" if keywords_found >= 1 else "Document Detected"

    # 4. Final verification checks using the stricter 85% threshold
    name_matching_verified = sim_score > 0.85
    license_detected = "Driver's License Detected" in doc_status or name_matching_verified
    
    if name_matching_verified:
        license_detected = True # Name match override
        print(f"🎯 Guest name match override: License detection forced to TRUE")

    guest_verified = helmet_verified and license_detected

    # Print final results (similar to the old function)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 EFFICIENT GUEST VERIFICATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🪖 Helmet: {'✅' if helmet_verified else '❌'}")
    print(f"📅 Expiration Date: {extracted_date or 'Not Found'}")
    print(f"🆔 License Detected: {'✅' if license_detected else '❌'}" +
          (" (Name Match Override)" if name_matching_verified else ""))
    print(f"👤 Name Match: {'✅' if name_matching_verified else '❌'} ({sim_score*100:.1f}%)")
    print(f"🟢 STATUS: {'✅ GUEST VERIFIED' if guest_verified else '❌ GUEST VERIFICATION FAILED'}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return guest_verified
