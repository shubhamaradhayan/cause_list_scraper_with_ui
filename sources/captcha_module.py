import cv2
from PIL import Image
import pytesseract
import requests
import os
class CaptchaSolver:
    def __init__(self, image_url=None, image_path=None):
        # self.image_path = image_path
        self.image_url = image_url  # Assuming image_path is a URL for downloading
        self.image_path = image_path   # Local path to save the downloaded image

    def download_image(self):
        save_path = 'captcha.png'
        response = requests.get(self.image_url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded as {self.image_path}")
        return save_path
    
    def preprocess_image(self):

        image_path =  self.image_path if self.image_path else self.download_image()
        # Read image with OpenCV
        img = cv2.imread(image_path)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Threshold to binary (adjust threshold value if needed)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Save temp image
        cv2.imwrite('processed.png', thresh)

    def solve_captcha(self):
        self.preprocess_image()
        # Run Tesseract on the processed image
        text = pytesseract.image_to_string(
            Image.open('processed.png'),
            config='--psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        )
        return text.strip()



