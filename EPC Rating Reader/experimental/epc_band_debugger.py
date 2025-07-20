import requests
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

# List of EPC image URLs to inspect
epc_urls = [
    "https://media.rightmove.co.uk/49k/48450/87165312/48450_YLK250003_EPCGRAPH_00_0000.png",
    "https://media.rightmove.co.uk/85k/84818/160279784/84818_33793810_EPCGRAPH_00_0000.png",
    "https://media.rightmove.co.uk/122k/121270/143378412/121270_EPCRM__EPCGRAPH_00_0000.png"
]

# Vertical bands to test
bands = [
    (0.00, 0.15), (0.15, 0.30), (0.30, 0.45),
    (0.45, 0.60), (0.60, 0.75), (0.75, 0.90), (0.90, 1.00)
]

def crop_column_band(image, x_start_ratio, x_end_ratio, y_start_ratio, y_end_ratio):
    width, height = image.size
    x1 = int(x_start_ratio * width)
    x2 = int(x_end_ratio * width)
    y1 = int(y_start_ratio * height)
    y2 = int(y_end_ratio * height)
    return image.crop((x1, y1, x2, y2))

def visualize_epc_bands(epc_url, column_x_start=0.70, column_x_end=1.00):
    response = requests.get(epc_url)
    img = Image.open(BytesIO(response.content)).convert("L")

    fig, axes = plt.subplots(1, len(bands), figsize=(3 * len(bands), 5))
    if len(bands) == 1:
        axes = [axes]

    for ax, (y_start, y_end) in zip(axes, bands):
        crop = crop_column_band(img, column_x_start, column_x_end, y_start, y_end)
        ax.imshow(crop, cmap='gray')
        ax.set_title(f"Y: {y_start:.2f}-{y_end:.2f}", fontsize=8)
        ax.axis("off")

    fig.suptitle(f"EPC Band Crop – {epc_url.split('/')[-1]}", fontsize=10)
    plt.tight_layout()
    plt.show()

# Run visualization on each EPC
for url in epc_urls:
    visualize_epc_bands(url)
