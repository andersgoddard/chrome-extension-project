from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
import requests
import base64
from io import BytesIO
from PIL import Image

class BaseOCREngine(ABC):
    @abstractmethod
    def readtext(self, image: np.ndarray) -> List[Tuple[Tuple[int, int, int, int], str, float]]:
        """
        Perform OCR on the given image and return a list of:
        (bounding_box, text, confidence)
        """
        pass

class EasyOCREngine(BaseOCREngine):
    def __init__(self):
        import easyocr
        self.reader = easyocr.Reader(['en'], gpu=False)

    def readtext(self, image: np.ndarray) -> List[Tuple[Tuple[int, int, int, int], str, float]]:
        return self.reader.readtext(image)

class TesseractOCREngine(BaseOCREngine):
    def __init__(self):
        import pytesseract
        from PIL import Image
        pytesseract.pytesseract.tesseract_cmd = r"C:\Users\agoddard\OneDrive - Kinleigh Folkard & Hayward\Documents\Data\Rightmove\tesseract_portable_windows-main\tesseract.exe"
        self.pytesseract = pytesseract
        self.Image = Image

    def readtext(self, image: np.ndarray) -> List[Tuple[Tuple[int, int, int, int], str, float]]:
        pil_img = self.Image.fromarray(image)
        data = self.pytesseract.image_to_data(pil_img, output_type=self.pytesseract.Output.DICT)

        output = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            conf = data['conf'][i]
            if text and conf != '-1':
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                bbox = (x, y, x + w, y + h)
                confidence = float(conf) / 100.0
                print(f"[DEBUG] Text: '{text}' | BBox: {bbox} | Confidence: {confidence:.2f}")
                output.append((bbox, text, confidence))
        return output

class ChatGPTEngine(BaseOCREngine):
    def __init__(self):
        """
        Initialize the ChatGPTEngine with the OpenAI API key and model.
        :param api_key: Your OpenAI API key
        :param model: The model to use for the API call (default is gpt-4)
        """
        self.api_key = "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"
        self.model = "gpt-4o"
        self.api_url = 'https://api.openai.com/v1/chat/completions'  # Use the correct endpoint for image analysis

    def readtext(self, image: np.ndarray) -> List[Tuple[Tuple[int, int, int, int], str, float]]:
        """
        Send the image directly to the ChatGPT API for analysis.
        """
        image_data = self._image_to_base64(image)
        ocr_data = self.send_to_api(image_data)
        return ocr_data

    def send_to_api(self, image_data: str):
        """
        Send image to the ChatGPT API for analysis (image-to-text processing).
        :param image_data: Base64 encoded image data
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # Prepare the payload
        payload = {
            "model": self.model,  # should be 'gpt-4o' or 'gpt-4-vision-preview'
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant analyzing image contents."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze the content of the image and give me the current and potential EPC ratings. Return this in a json format with current_epc and potential_epc as the keys"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
        }
    ],
    "max_tokens": 300
}


        # Send the request to the API
        response = requests.post(self.api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("Successfully sent image to ChatGPT API.")
            print(result.get('data', []))
            return result.get('data', [])
        else:
            print(f"Error sending data to API: {response.status_code}, {response.text}")
            return []

    def _image_to_base64(self, image: np.ndarray) -> str:
        """
        Convert the image (numpy array) to a base64 encoded string.
        :param image: The image in numpy array format.
        :return: The base64 encoded image string.
        """
        pil_image = Image.fromarray(image)  # Convert the NumPy array to a PIL image
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")  # Save the image as PNG in a BytesIO buffer
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')  # Encode the image to base64
        return img_base64