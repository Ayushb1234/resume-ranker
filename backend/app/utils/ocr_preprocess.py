import cv2
import numpy as np
import tempfile
import platform
from typing import List, Tuple

from pdf2image import convert_from_path

# -----------------------------
# Poppler configuration (Windows fix)
# -----------------------------
POPPLER_PATH = None

if platform.system() == "Windows":
    POPPLER_PATH = r"D:\programming\programming\python\age&genderdetection\yolov9\Resume History\Release-25.12.0-0\poppler-25.12.0\Library\bin"
    # ^ change ONLY if your poppler path is different


# -----------------------------
# PDF → Images
# -----------------------------
def pdf_to_images(pdf_path: str, dpi: int = 300) -> List[Tuple[str, int]]:
    """
    Converts PDF to PNG images.
    Returns list of (image_path, page_number)
    """
    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        poppler_path=POPPLER_PATH
    )

    output = []
    for i, img in enumerate(images):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(tmp.name, format="PNG")
        output.append((tmp.name, i + 1))

    return output


# -----------------------------
# Image preprocessing for OCR
# -----------------------------
def preprocess_image(path: str, out_path: str | None = None) -> str:
    """
    OpenCV preprocessing:
    - grayscale
    - denoise
    - contrast enhancement (CLAHE)
    - adaptive threshold
    - deskew
    """
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Cannot read image: {path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        15,
        6
    )

    # Deskew
    coords = np.column_stack(np.where(thresh > 0))
    if coords.size > 0:
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle

        h, w = thresh.shape
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        thresh = cv2.warpAffine(
            thresh,
            matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

    output_path = out_path or path
    cv2.imwrite(output_path, thresh)

    return output_path
