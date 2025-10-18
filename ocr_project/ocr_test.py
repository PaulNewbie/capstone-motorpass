# ocr_test.py

import os
from license_reader import licenseRead
import time

def run_ocr_test():
    """
    Tests the licenseRead function (now using EasyOCR) with a sample image.
    """
    # --- CONFIGURATION ---
    test_image_path = "IMG_20250624_141338.jpg"
    mock_fingerprint_data = {
        'name': 'PUNZAL, PAUL JOHN HACLA',
        'id': '2021000001',
        'confidence': 95
    }
    # --- END CONFIGURATION ---

    print("=========================================")
    print("      MOTORPASS OCR ACCURACY TESTER      ")
    print("         (Using EasyOCR Engine)          ")
    print("=========================================\n")

    if not os.path.exists(test_image_path):
        print(f"❌ ERROR: Test image not found at '{test_image_path}'")
        return

    print(f"📄 Testing with image: '{test_image_path}'")
    print(f"👤 Mock reference name: '{mock_fingerprint_data['name']}'\n")

    try:
        start_time = time.time()
        result = licenseRead(test_image_path, mock_fingerprint_data)
        end_time = time.time()

        # --- Display Results ---
        print("---------- OCR RESULTS ----------\n")
        print(f"👤 Extracted Name:       {result.name}")
        print(f"📅 Expiration Date:      {result.expiration_date if result.expiration_date else 'Not Found'}")
        print(f"✅ Is Expired:           {result.is_expired if result.is_expired is not None else 'N/A'}")
        print(f"📄 Document Status:      {result.document_verified}")
        print(f"💯 Name Match Score:     {result.match_score * 100:.2f}%" if result.match_score is not None else "N/A")
        print(f"⏱️ Processing Time:      {end_time - start_time:.2f} seconds")

        print("\n---------- RAW OCR TEXT ----------\n")
        print(result.formatted_text)
        print("\n----------------------------------\n")

        # --- Verdict ---
        print("---------- VERDICT ----------\n")
        if result.name != "Not Found" and result.expiration_date and result.is_expired is False:
            print("✅ SUCCESS: Name and valid expiration date were extracted successfully.")
        else:
            print("❌ FAILURE: Could not reliably extract all required information.")

    except Exception as e:
        print(f"\nAn unexpected error occurred during the test: {e}")

    print("\n=========================================")
    print("            TEST COMPLETE            ")
    print("=========================================")


if __name__ == "__main__":
    run_ocr_test()
