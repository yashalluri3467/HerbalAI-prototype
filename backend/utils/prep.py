import cv2
import numpy as np
import torch
from PIL import Image

def preprocess_image_pipeline(image_path_or_bytes, size=(224, 224)):
    """
    Complete image preprocessing pipeline:
    1. Load image (RGB)
    2. Apply Denoising
    3. Apply Contrast Enhancement (CLAHE)
    4. Resize
    5. Convert to tensor and Normalize
    Returns:
        preprocessed_tensor: PyTorch tensor [1, 3, H, W]
        bgr_original: original opencv BGR image for Grad-CAM overlay
        bgr_enhanced: enhanced opencv BGR image to show preprocessing on frontend
    """
    # 1. Load image
    if isinstance(image_path_or_bytes, str):
        # Image path
        img = cv2.imread(image_path_or_bytes)
    else:
        # Image bytes
        nparr = np.frombuffer(image_path_or_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
    if img is None:
        raise ValueError("Could not decode image")
        
    bgr_original = img.copy()
    
    # 2. Denoising
    # Use bilateral filter to denoise while keeping edges sharp (great for lesions/leaves)
    denoised = cv2.bilateralFilter(bgr_original, d=9, sigmaColor=75, sigmaSpace=75)
    
    # 3. Contrast Enhancement (CLAHE on L channel of LAB color space)
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    lab_enhanced = cv2.merge((l_enhanced, a, b))
    bgr_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    
    # 4. Resize
    resized = cv2.resize(bgr_enhanced, size)
    
    # Convert BGR to RGB for PyTorch model
    rgb_resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    
    # 5. Convert to tensor and Normalize
    # Scale to [0, 1]
    img_float = rgb_resized.astype(np.float32) / 255.0
    
    # Normalize mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_normalized = (img_float - mean) / std
    
    # [H, W, C] -> [C, H, W]
    img_tensor = img_normalized.transpose((2, 0, 1))
    
    # Add batch dimension [1, C, H, W]
    input_tensor = torch.tensor(img_tensor).unsqueeze(0)
    
    return input_tensor, bgr_original, bgr_enhanced
