from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np

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
