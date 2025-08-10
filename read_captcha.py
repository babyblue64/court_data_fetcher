#! /usr/bin/env python3

import cv2
import pytesseract
import random

def quick_read_captcha(image_path):
    """
    Quick function to read a single CAPTCHA image and ensure the output is always a 6-digit number.
    If the read text is shorter than 6 digits, it will be padded with random digits.
    """
    try:
        # Read and preprocess
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
        
        # Resize for better OCR
        height, width = thresh.shape
        resized = cv2.resize(thresh, (width * 2, height * 2))
        
        # Extract text (digits only)
        config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
        text = pytesseract.image_to_string(resized, config=config).strip()
        
        # Ensure the result is a 6-digit number
        if len(text) >= 6:
            return text[:6]  # Take first 6 digits if longer
        else:
            # Pad with random digits to make it 6 digits
            missing_digits = 6 - len(text)
            random_digits = ''.join(random.choice('0123456789') for _ in range(missing_digits))
            return text + random_digits
            
    except Exception as e:
        print(f"Error: {e}")
        # Return a random 6-digit number in case of error
        return ''.join(random.choice('0123456789') for _ in range(6))

if __name__ == "__main__":
    result = quick_read_captcha("captcha.png")
    print(f"Quick result: {result}")