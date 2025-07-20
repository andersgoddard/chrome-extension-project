import requests
import re
import numpy as np
import time
import cv2

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button

from io import BytesIO
from PIL import Image, ImageEnhance, ImageOps

from helpers.epc_image_preprocessing import preprocess_image
from helpers.epc_image_preprocessing import preserve_white_only
from helpers.ocr_engine_loader import OCREngine

min_valid_epc = 10
max_valid_epc = 100

def download_image(url: str, max_retries=5, delay_seconds=2, cache_path="data/latest_epc.png") -> Image.Image:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(cache_path, "wb") as f:
                f.write(response.content)
            print(f"⬇️ EPC image cached as: {cache_path}")
            return Image.open(cache_path).convert("RGB")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(delay_seconds)

    raise Exception(f"❌ Failed to download image after {max_retries} attempts: {url}")

def crop_column_band(image, x_start_ratio, x_end_ratio, y_start_ratio, y_end_ratio):
    width, height = image.size
    x1 = int(x_start_ratio * width)
    x2 = int(x_end_ratio * width)
    y1 = int(y_start_ratio * height)
    y2 = int(y_end_ratio * height)
    return image.crop((x1, y1, x2, y2))

def prompt_dual_epc_input_with_gui(image):
    fig, ax = plt.subplots(figsize=(6, 8))
    fig, ax = plt.subplots(figsize=(6, 8))
    plt.subplots_adjust(bottom=0.3)
    ax.imshow(image, cmap='gray')
    ax.set_title("Enter EPC Ratings Below")
    ax.axis('off')

    text_ax_current = plt.axes([0.25, 0.15, 0.2, 0.05])
    text_box_current = TextBox(text_ax_current, "Current EPC", initial="")

    text_ax_potential = plt.axes([0.55, 0.15, 0.2, 0.05])
    text_box_potential = TextBox(text_ax_potential, "Potential EPC", initial="")

    button_ax = plt.axes([0.4, 0.05, 0.2, 0.05])
    button = Button(button_ax, "Submit")

    user_input = {"current": None, "potential": None}

    def submit(event):
        try:
            val_current = int(text_box_current.text.strip())
            val_potential = int(text_box_potential.text.strip())
            user_input["current"] = val_current
            user_input["potential"] = val_potential
            plt.close()
        except ValueError:
            text_box_current.set_val("")
            text_box_potential.set_val("")

    button.on_clicked(submit)
    plt.show()

    return user_input["current"], user_input["potential"]

def generate_overlapping_bands(band_height=0.15, overlap=0.05):
    y_start = 0.0
    bands = []
    while y_start < 1.0:
        y_end = min(y_start + band_height, 1.0)
        bands.append((y_start, y_end))
        y_start += (band_height - overlap)
    return bands

def generate_variants(crop_pil: Image.Image):
    base_array = np.array(crop_pil)
    variants = [("standard", preprocess_image(base_array))]

    for contrast in [1.8, 2.2, 2.5]:
        for brightness in [20, 40]:
            for invert in [True, False]:
                enhanced = ImageEnhance.Contrast(crop_pil).enhance(contrast)
                enhanced = ImageEnhance.Brightness(enhanced).enhance(1 + brightness / 100.0)
                if invert:
                    enhanced = ImageOps.invert(enhanced)
                arr = preprocess_image(np.array(enhanced))
                label = f"contrast={contrast}, brightness={brightness}, invert={invert}"
                variants.append((label, arr))
    return variants

def extract_candidates(reader, image, x_start, x_end, label):
    bands = generate_overlapping_bands(band_height=0.20, overlap=0.10)
    candidates = []

    for y_start, y_end in bands:
        crop_pil = crop_column_band(image, x_start, x_end, y_start, y_end)
        crop_array = np.array(crop_pil)

        # 🔍 QUICK SCAN — early catch from raw image
        quick_results = reader.readtext(crop_array)
        for box, text, conf in quick_results:
            digits = re.findall(r'\d{2}', text)
            if digits and conf >= 0.80:
                for num_str in digits:
                    num = int(num_str)
                    candidates.append((num, conf))
                    print(f"[QUICK SCAN] Found {num} with conf {conf:.2f} in raw band")
                    if min_valid_epc <= num <= max_valid_epc:
                        return [(num, conf)]

        # 🧪 FULL PREPROCESSING — fallback if quick scan misses
        variants = generate_variants(crop_pil)
        found_in_variants = False

        for label, processed in variants:
            results = reader.readtext(processed)
#            print(f"\n[OCR-{label}] Raw OCR Output: {results}")
            for _, text, conf in results:
#                print(f"[OCR-{label}] Parsed Text: '{text}' | Conf: {conf:.2f}")
                found = re.findall(r'\d+', text)
#                print(f"[OCR-{label}] Digits Extracted: {found}")
                for num_str in found:
                    num = int(num_str)
                    candidates.append((num, conf))
                    found_in_variants = True
                    print(f"[OCR-{label}] ✔ Added {num} with confidence {conf:.2f}")
                    if conf >= 0.80 and min_valid_epc <= num <= max_valid_epc:
                        return [(num, conf)]

        # 🛟 RESCUE MODE — if no digits found and crop is bright
        if not found_in_variants and np.max(crop_array) > 200:
            rescue_img = preserve_white_only(crop_array)
            rescue_results = reader.readtext(rescue_img)
#            print("\n[RESCUE MODE] Raw OCR:", rescue_results)
            for _, text, conf in rescue_results:
 #               print(f"[RESCUE MODE] Parsed: '{text}' | Conf: {conf:.2f}")
                found = re.findall(r'\d+', text)
  #              print(f"[RESCUE MODE] Digits Found: {found}")
                for num_str in found:
                    num = int(num_str)
                    candidates.append((num, conf))
                    print(f"[RESCUE MODE] ✔ Added {num} with conf {conf:.2f}")
                    if conf >= 0.90 and min_valid_epc <= num <= max_valid_epc:
                        return [(num, conf)]

    return candidates

def validate_epc_value(candidates):
    for value, conf in sorted(candidates, key=lambda x: -x[1]):
        if min_valid_epc <= value <= max_valid_epc:
            return value, conf
    return None, None

def extract_epc_scores(url, reader):
    image = download_image(url)

    current_candidates = extract_candidates(reader, image, 0.70, 0.82, "current")
    current_epc, current_conf = validate_epc_value(current_candidates)
    manual_current = current_conf is None
    potential_candidates = extract_candidates(reader, image, 0.82, 1.00, "potential")
    potential_epc, potential_conf = validate_epc_value(potential_candidates)
    manual_potential = potential_conf is None
    needs_manual = (
        manual_current or manual_potential or
        current_epc is None or potential_epc is None or
        current_epc < min_valid_epc or current_epc > max_valid_epc or
        potential_epc < min_valid_epc or potential_epc > max_valid_epc or
        potential_epc < current_epc
    )

    if needs_manual:
        print("\n⚠️ Manual input required due to validation failure.")
        current_epc, potential_epc = prompt_dual_epc_input_with_gui(image)
        current_conf = potential_conf = "manual"
        manual_current = manual_potential = True

    print(f"\n🧾 Final EPC values:\n  Current: {current_epc}\n  Potential: {potential_epc}")
    return current_epc, potential_epc, current_conf, potential_conf, manual_current, manual_potential
