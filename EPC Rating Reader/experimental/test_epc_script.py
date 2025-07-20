import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import re
import time

from read_epc import extract_epc_scores  # Your core EPC extraction logic
from helpers.ocr_engine_loader import OCREngine

# 🖼 Debug visualizer for EPC chunks
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

# 👀 GUI for manual review
def review_prediction_gui(image_url, current, potential):
    img = Image.open("data/latest_epc.png").convert("L")

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

# 🔄 Loop through EPC URLs and process
input_file = "data/epc_links.xlsx"
df = pd.read_excel(input_file, engine='openpyxl')
reader = OCREngine()
results = []

for index, row in df.iterrows():
    url = row[0]
    print(f"\n🔍 Processing: {url}")
    try:
        # debug_visualize_chunks(image_pil)  # 🌟 Show chunks being scanned

        current, potential, conf_current, conf_potential, manual_current, manual_potential = extract_epc_scores(url, reader)
        feedback = review_prediction_gui(url, current, potential)

        results.append({
            "Image URL": url,
            "Current EPC": current,
            "Potential EPC": potential,
            "Confidence (Current)": conf_current,
            "Confidence (Potential)": conf_potential,
            "Manual Input (Current)": "yes" if manual_current else "no",
            "Manual Input (Potential)": "yes" if manual_potential else "no",
            "User Confirmed Prediction": feedback
        })
    except Exception as e:
        print(f"❌ Error processing {url}: {e}")
        results.append({
            "Image URL": url,
            "Current EPC": "error",
            "Potential EPC": "error",
            "Confidence (Current)": "error",
            "Confidence (Potential)": "error",
            "Manual Input (Current)": "error",
            "Manual Input (Potential)": "error",
            "User Confirmed Prediction": "error"
        })

# 💾 Save the output
output_file = "tests/epc_results.xlsx"
pd.DataFrame(results).to_excel(output_file, index=False, engine='openpyxl')
print(f"\n✅ Results saved to: {output_file}")
