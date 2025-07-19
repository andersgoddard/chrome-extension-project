import easyocr
import requests
from io import BytesIO
from PIL import Image
import numpy as np

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Download image from URL
def download_image(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")

# Run OCR and print all text
def extract_all_text_from_epc(url: str):
    image_pil = download_image(url)
    image_np = np.array(image_pil)

    results = reader.readtext(image_np)
    print(f"\n🔍 OCR Results from EPC Image:")
    for box, text, conf in results:
        print(f"- Text: '{text}' | Confidence: {conf:.2f} | Box: {box}")

# 🚀 Replace with your EPC image URL
epc_url = "https://media.rightmove.co.uk/85k/84818/161654702/84818_33867661_EPCGRAPH_00_0000.png"
extract_all_text_from_epc(epc_url)
