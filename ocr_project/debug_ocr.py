# debug_ocr.py

import requests
import os

# --- Configuration ---
# PASTE YOUR FREE API KEY HERE from https://ocr.space/ocrapi/free
OCR_SPACE_API_KEY = 'K86208907288957' # <--- REPLACE WITH YOUR KEY
IMAGE_FILE_PATH = 'IMG_20250624_141338.jpg'
OCR_SPACE_URL = 'https://api.ocr.space/parse/image'
# --- End Configuration ---

def run_debug_test():
    """
    A dedicated script to debug file loading and the OCR API call.
    """
    print("=========================================")
    print("         OCR FILE LOADING DEBUGGER         ")
    print("=========================================\n")

    # 1. Check if the API key has been changed
    if 'K81234567888957' in OCR_SPACE_API_KEY:
        print("❌ ERROR: Please replace 'K81234567888957' with your actual free API key from OCR.space.")
        return

    # 2. Check if the image file exists
    print(f"Checking for image file at: '{os.path.abspath(IMAGE_FILE_PATH)}'")
    if not os.path.exists(IMAGE_FILE_PATH):
        print("❌ CRITICAL ERROR: The image file was not found at this path.")
        print("   Please ensure the image and this script are in the same folder.")
        return
    
    print("✅ File found.")

    # 3. Check the size of the image file
    try:
        file_size = os.path.getsize(IMAGE_FILE_PATH)
        print(f"✅ File size is: {file_size} bytes.")
        if file_size < 10000: # A decent photo should be > 10KB
            print("   ⚠️ WARNING: The file size is very small. The file may be empty or corrupted.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Could not get the file size. Error: {e}")
        return

    # 4. Attempt to send the file to the OCR API
    print("\nAttempting to send image to OCR.space API...")
    try:
        with open(IMAGE_FILE_PATH, 'rb') as f:
            payload = {'apikey': OCR_SPACE_API_KEY, 'language': 'eng', 'scale': 'true', 'OCREngine': 2}
            files_to_send = {'filename': (os.path.basename(IMAGE_FILE_PATH), f, 'image/jpeg')}
            
            response = requests.post(OCR_SPACE_URL, files=files_to_send, data=payload)
            response.raise_for_status() # Check for network errors (like 404, 500)

        print("✅ Successfully sent request to the API.")
        
        # 5. Analyze the API response
        print("\n--- API RESPONSE ---")
        result = response.json()
        print(result)
        print("--------------------\n")

        if result.get('IsErroredOnProcessing'):
            print("❌ API ERROR: The OCR service reported an error.")
            print(f"   Error Message: {result.get('ErrorMessage')}")
        elif result.get('ParsedResults'):
            parsed_text = result['ParsedResults'][0]['ParsedText']
            print("✅ SUCCESS: The API returned the following text:\n")
            print("--- PARSED TEXT ---")
            print(parsed_text)
            print("-------------------")
        else:
            print("❌ UNKNOWN ERROR: The API response was not in the expected format.")

    except requests.exceptions.RequestException as e:
        print(f"❌ CRITICAL NETWORK ERROR: Could not connect to the OCR API. Error: {e}")
    except Exception as e:
        print(f"❌ AN UNEXPECTED SCRIPT ERROR OCCURRED: {e}")

    print("\n=========================================")
    print("            DEBUG COMPLETE             ")
    print("=========================================")

if __name__ == "__main__":
    run_debug_test()
