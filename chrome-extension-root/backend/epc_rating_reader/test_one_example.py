from epc_rating_reader import fetch_epc_ratings
from ocr_engine_loader import OCREngine 

def main():
    epc_url = "https://media.rightmove.co.uk/31k/30575/164542931/30575_05310827_EPCGRAPH_00_0000.jpeg"
    reader = OCREngine()

    current, potential = fetch_epc_ratings(epc_url, reader)

    print(f"Current EPC Score: {current}")
    print(f"Potential EPC Score: {potential}")

if __name__ == "__main__":
    main()
