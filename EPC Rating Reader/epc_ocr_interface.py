import numpy as np
import requests
import json
import base64
import re
import os 

from abc import ABC, abstractmethod
from typing import List, Tuple
from io import BytesIO
from PIL import Image
from openai import OpenAI

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
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Vision-capable model

    def readtext(self, image_url: str):
        """
        Sends an image URL plus prompt to the GPT vision model,
        returns parsed JSON or raw string response.
        """
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that reads and extracts data from EPC graphs."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this EPC image and return current and potential EPC ratings in JSON. I only need the numeric ratings and please use only current and potential as keys. Sometimes there are two charts, in which case the one to look at is the Energy Efficiency Rating chart."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=300,
        )

        content = response.choices[0].message.content
        print("[DEBUG] API response content:", content)

        # Extract the JSON block between triple backticks
        match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            json_text = match.group(1)
            try:
                data = json.loads(json_text)
                return data
            except json.JSONDecodeError:
                print("Failed to parse JSON block.")
                return json_text
        else:
            print("No JSON block found. Returning raw content.")
            return content