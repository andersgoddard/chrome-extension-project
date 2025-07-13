import matplotlib.pyplot as plt
from PIL import Image

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

def download_image(url: str) -> Image.Image:
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")
