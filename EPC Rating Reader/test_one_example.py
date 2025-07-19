from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import requests
from io import BytesIO

from read_epc import extract_epc_scores
from helpers.ocr_engine_loader import OCREngine

# 🖼 Debug visualizer (optional)
def debug_visualize_chunks(image_pil, x_start=0.70, x_end=1.00, band_height=0.20, overlap=0.10):
    width, height = image_pil.size
    bands = []
    y_start = 0.0
    while y_start < 1.0:
        y_end = min(y_start + band_height, 1.0)
        bands.append((y_start, y_end))
        y_start += (band_height - overlap)

    fig, axes = plt.subplots(1, len(bands), figsize=(3 * len(bands), 5))
    if len(bands) == 1:
        axes = [axes]

    for ax, (y1_ratio, y2_ratio) in zip(axes, bands):
        x1 = int(x_start * width)
        x2 = int(x_end * width)
        y1 = int(y1_ratio * height)
        y2 = int(y2_ratio * height)
        crop = image_pil.crop((x1, y1, x2, y2))
        ax.imshow(crop, cmap='gray')
        ax.set_title(f"Y: {y1_ratio:.2f}–{y2_ratio:.2f}", fontsize=8)
        ax.axis("off")

    fig.suptitle("EPC Chunk Regions", fontsize=12)
    plt.tight_layout()
    plt.show()

# 👀 Manual review GUI
def review_prediction_gui(image_path, current, potential):
    img = Image.open(image_path).convert("L")

    fig, ax = plt.subplots(figsize=(6, 8))
    plt.subplots_adjust(bottom=0.2)
    ax.imshow(img, cmap='gray')
    ax.set_title(f"Predicted EPC Ratings\nCurrent: {current}, Potential: {potential}")
    ax.axis('off')

    feedback = {"confirmed": None}

    def confirm(event):
        feedback["confirmed"] = "yes"
        plt.close()

    def reject(event):
        feedback["confirmed"] = "no"
        plt.close()

    ax_confirm = plt.axes([0.25, 0.05, 0.2, 0.075])
    btn_confirm = Button(ax_confirm, "Correct")
    btn_confirm.on_clicked(confirm)

    ax_reject = plt.axes([0.55, 0.05, 0.2, 0.075])
    btn_reject = Button(ax_reject, "Incorrect")
    btn_reject.on_clicked(reject)

    plt.show()
    return feedback["confirmed"]

# 🔍 Hardcoded EPC image URL
epc_url = "https://media.rightmove.co.uk/31k/30575/164542931/30575_05310827_EPCGRAPH_00_0000.jpeg"
print(f"\n🔍 Processing: {epc_url}")

# Download and save for GUI display
response = requests.get(epc_url)
image = Image.open(BytesIO(response.content))
image.save("data/latest_epc.png")  # GUI expects this filename

# 🔡 OCR and extraction
reader = OCREngine()

try:
    current, potential, conf_current, conf_potential, manual_current, manual_potential = extract_epc_scores(epc_url, reader)
    feedback = review_prediction_gui("data/latest_epc.png", current, potential)

    print("\n✅ Result:")
    print(f"  Current EPC: {current}")
    print(f"  Potential EPC: {potential}")
    print(f"  Confidence (Current): {conf_current}")
    print(f"  Confidence (Potential): {conf_potential}")
    print(f"  Manual Input (Current): {'yes' if manual_current else 'no'}")
    print(f"  Manual Input (Potential): {'yes' if manual_potential else 'no'}")
    print(f"  User Confirmed Prediction: {feedback}")
except Exception as e:
    print(f"❌ Error processing EPC image: {e}")
