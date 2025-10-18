# final_test.py

import requests
import os
import re
import difflib
from PIL import Image # Using the Pillow library for robust image handling
from io import BytesIO

# --- Configuration ---
# PASTE YOUR FREE API KEY HERE from https://ocr.space/ocrapi/free
OCR_SPACE_API_KEY = 'K86208907288957' # <--- REPLACE WITH YOUR KEY
IMAGE_FILE_PATH = 'IMG_20250624_141338.jpg'
OCR_SPACE_URL = 'https://api.ocr.space/parse/image'
MOCK_REFERENCE_NAME = 'PUNZAL, PAUL JOHN HACLA'
# --- End Configuration ---

def run_final_test():
    """
    A definitive test using Pillow to handle the image and the OCR.space API.
    """
    print("=========================================")
    print("     MOTORPASS OCR - FINAL TEST SCRIPT     ")
    print("=========================================\n")

    if 'K81234567888957' in OCR_SPACE_API_KEY:
        print("❌ ERROR: Please replace 'K81234567888957' with your actual API key.")
        return

    if not os.path.exists(IMAGE_FILE_PATH):
        print(f"❌ ERROR: Cannot find image file: {IMAGE_FILE_PATH}")
        return

    try:
        # --- Robust Image Handling using Pillow ---
        print(f"Opening image with Pillow: {IMAGE_FILE_PATH}")
        with Image.open(IMAGE_FILE_PATH) as img:
            # Resize to a reasonable size to ensure it's under the API limit
            img.thumbnail((1500, 1500))
            
            # Save the resized image to an in-memory byte stream
            output_buffer = BytesIO()
            img.save(output_buffer, format='JPEG')
            image_bytes = output_buffer.getvalue()
        
        print(f"✅ Image loaded and resized successfully. Size: {len(image_bytes)} bytes.")

        # --- Sending to API ---
        print("Sending clean image data to OCR.space API...")
        payload = {'apikey': OCR_SPACE_API_KEY, 'language': 'eng', 'scale': 'true', 'OCREngine': 2}
        files = {'file': ('license.jpg', image_bytes, 'image/jpeg')}
        
        response = requests.post(OCR_SPACE_URL, files=files, data=payload)
        response.raise_for_status()
        result = response.json()

        if result.get('IsErroredOnProcessing'):
            raise RuntimeError(f"API Error: {result.get('ErrorMessage')}")

        raw_text = result['ParsedResults'][0]['ParsedText']
        print("✅ API returned successful response.")

        # --- Data Extraction (simplified for this test) ---
        expiration_date = re.search(r'(20\d{2}[-/\s]?\d{2}[-/\s]?\d{2})', raw_text)
        expiration_date = expiration_date.group(0) if expiration_date else "Not Found"

        name_found = "Not Found"
        if MOCK_REFERENCE_NAME.split(',')[0] in raw_text:
             name_found = MOCK_REFERENCE_NAME # Simple check for the test

        print("\n---------- OCR RESULTS ----------\n")
        print(f"👤 Extracted Name:       {name_found}")
        print(f"📅 Expiration Date:      {expiration_date}")
        
        print("\n---------- RAW OCR TEXT ----------\n")
        print(raw_text)
        print("\n----------------------------------\n")
        
        if name_found != "Not Found" and expiration_date != "Not Found":
            print("✅ SUCCESS: Required information was extracted.")
        else:
            print("❌ FAILURE: Could not extract all required information from the text.")


    except Exception as e:
        print(f"❌ AN ERROR OCCURRED: {e}")

    print("\n=========================================")
    print("            TEST COMPLETE            ")
    print("=========================================")


if __name__ == "__main__":
    run_final_test()
