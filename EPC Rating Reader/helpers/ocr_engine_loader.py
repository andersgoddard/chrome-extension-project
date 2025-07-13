from epc_ocr_interface import EasyOCREngine, TesseractOCREngine

def OCREngine():
    try:
        with open("ocr_engine.txt", "r") as f:
            engine_name = f.read().strip().lower()
    except FileNotFoundError:
        engine_name = "easyocr"

    engine_map = {
        "easyocr": EasyOCREngine,
        "tesseract": TesseractOCREngine
    }

    return engine_map.get(engine_name, EasyOCREngine)()
