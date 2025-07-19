import cv2
import numpy as np

def to_grayscale(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def enhance_contrast(image: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)

def brighten_image(image: np.ndarray, alpha: float = 1.2, beta: int = 30) -> np.ndarray:
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def binarize_image(image: np.ndarray) -> np.ndarray:
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def remove_noise(image: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoising(image, None, h=30)

def preprocess_image(image: np.ndarray) -> np.ndarray:
    gray = to_grayscale(image)
    contrast = enhance_contrast(gray)
    bright = brighten_image(contrast)
    denoised = remove_noise(bright)
    binary = binarize_image(denoised)
    return binary

def preserve_white_only(image: np.ndarray) -> np.ndarray:
    # Ensure RGB
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Threshold for "white-ish"
    lower_white = np.array([200, 200, 200], dtype=np.uint8)
    upper_white = np.array([255, 255, 255], dtype=np.uint8)

    # Mask white pixels
    mask = cv2.inRange(image, lower_white, upper_white)

    # Create binary output: white stays, everything else becomes black
    output = np.zeros_like(mask)
    output[mask > 0] = 255

    return output
