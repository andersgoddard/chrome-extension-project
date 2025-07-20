from epc_rating_reader.epc_ocr_interface import EasyOCREngine, TesseractOCREngine, ChatGPTEngine

def OCREngine():
    try:
        with open("ocr_engine.txt", "r") as f:
            engine_name = f.read().strip().lower()
            print(engine_name)
    except FileNotFoundError:
        engine_name = "chatgpt"
        print(engine_name)

    engine_map = {
        "easyocr": EasyOCREngine,
        "tesseract": TesseractOCREngine,
        "chatgpt": ChatGPTEngine
    }

    return engine_map.get(engine_name, EasyOCREngine)()
