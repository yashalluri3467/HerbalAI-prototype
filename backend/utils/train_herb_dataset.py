import os
import sys
import argparse
import re
import unicodedata
from pathlib import Path
import cv2
import numpy as np

# Ensure the project root (backend) is on the Python path for module imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from utils.prep import preprocess_image_pipeline

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image

from models.classifiers import HerbClassifier

# Mapping of common synonyms to standard HERB_CLASSES names if possible
HERB_SYNONYMS = {
    "neem": "Neem",
    "azadirachta indica": "Neem",
    "aloe vera": "Aloe Vera",
    "turmeric": "Turmeric",
    "curcuma longa": "Turmeric",
    "curcuma caesia": "Turmeric",
    "curcuma zedoaria": "Turmeric",
    "tulsi": "Tulsi",
    "ocimum tenuiflorum": "Tulsi",
    "ocimum basilicum": "Tulsi",
    "ocimum americanum": "Tulsi",
    "amla": "Amla",
    "phyllanthus emblica": "Amla",
    "harra": "Harra",
    "terminalia chebula": "Harra",
    "bahera": "Bahera",
    "terminalia bellirica": "Bahera",
    "giloy": "Giloy",
    "tinospora cordifolia": "Giloy",
    "mahua": "Mahua",
    "madhuca longifolia": "Mahua",
    "karanj": "Karanj",
    "pongamia pinnata": "Karanj",
    "palash": "Palash",
    "butea monosperma": "Palash",
    "moringa": "Moringa",
    "moringa oleifera": "Moringa",
    "hibiscus": "Hibiscus",
    "hibiscus rosasinensis": "Hibiscus",
    "hibiscus rosa-sinensis": "Hibiscus",
    "ashwagandha": "Ashwagandha",
    "withania somnifera": "Ashwagandha",
    "bael": "Bael",
    "aegle marmelos": "Bael",
    "arjun": "Arjun",
    "terminalia arjuna": "Arjun",
    "chironji": "Chironji",
    "buchanania lanzan": "Chironji",
    "bhringraj": "Bhringraj",
    "eclipta prostrata": "Bhringraj",
    "bringaraja": "Bhringraj"
}

def clean_name(name):
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    name = name.lower().strip()
    return name

def parse_folder_name(folder_name):
    cleaned = clean_name(folder_name)
    
    # Check synonyms
    for pattern, std_name in HERB_SYNONYMS.items():
        if pattern in cleaned:
            return std_name
            
    # Extract all parentheses contents
    parentheses = re.findall(r'\(([^)]+)\)', folder_name)
    if parentheses:
        # Check from right to left
        for candidate in reversed(parentheses):
            cand_clean = candidate.strip().lower()
            # Skip short authors like (L.), (L), (Linn.), (Burm.F.)
            if len(cand_clean) > 3 and cand_clean not in {"linn", "linn.", "gaertn", "gaertn."}:
                return candidate.strip().title()
                
    # If no parentheses or no valid candidates, use the scientific name before any parenthesis/brackets
    sci = re.split(r'[\(\[\(]', folder_name)[0].strip()
    sci = re.sub(r'\s+', ' ', sci)
    # Strip common botanical suffixes
    sci = re.sub(r'\s+(l\.|var\.|corrêa|medik|willd|roxb|gaertn|lou.|sims|link|l)\.?$', '', sci, flags=re.IGNORECASE)
    return sci.title()

class HerbLeafDataset(Dataset):
    def __init__(self, root_dir: str, max_samples_per_class: int = 50, transform=None):
        # Resolve path and normalize any doubled backslashes from command line arguments
        root_dir = root_dir.replace("\\\\", "\\")
        self.root_dir = Path(root_dir)
        self.transform = transform or transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
        
        # Scan for species subfolders
        # We check if there are standard subfolders under root
        subdirs_to_scan = []
        raw_set = self.root_dir / "Raw leaf image set of Medicinal plants_v2"
        seg_set = self.root_dir / "Segmented leaf set using UNET segmentation"
        
        if raw_set.exists() and raw_set.is_dir():
            subdirs_to_scan.append(raw_set)
        if seg_set.exists() and seg_set.is_dir():
            subdirs_to_scan.append(seg_set)
            
        if not subdirs_to_scan:
            # If no nested raw/segmented directories exist, search the root directly
            subdirs_to_scan.append(self.root_dir)
            
        print(f"Scanning directories: {[str(p) for p in subdirs_to_scan]}")
        
        # First gather all class folders and unify their names
        class_folders_map = {} # unified_class_name -> list of Path objects
        for scan_dir in subdirs_to_scan:
            for d in scan_dir.iterdir():
                if d.is_dir():
                    unified = parse_folder_name(d.name)
                    if unified not in class_folders_map:
                        class_folders_map[unified] = []
                    class_folders_map[unified].append(d)
                    
        # Sort unified class names so mapping is deterministic
        self.classes = sorted(list(class_folders_map.keys()))
        self.class_to_idx = {name: i for i, name in enumerate(self.classes)}
        
        self.samples = []
        for unified_class, folders in class_folders_map.items():
            class_idx = self.class_to_idx[unified_class]
            class_samples = []
            
            # Find all image files under all folder mappings for this class
            for folder in folders:
                for img_path in folder.glob("*"):
                    if img_path.is_file() and img_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                        class_samples.append(img_path)
            
            # Optionally limit samples per class to speed up CPU training
            if max_samples_per_class > 0 and len(class_samples) > max_samples_per_class:
                class_samples = class_samples[:max_samples_per_class]
                
            for img_path in class_samples:
                self.samples.append((img_path, class_idx))
                
        if not self.samples:
            raise RuntimeError(f"No image files found in {root_dir}")
            
        print(f"Dataset initialized with {len(self.classes)} classes and {len(self.samples)} total samples.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        try:
            # Read image using Python file open and decode with cv2 to support unicode paths on Windows
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError(f"Could not decode image {img_path}")
            
            # 1. Resize first to speed up bilateral filtering!
            img_resized = cv2.resize(img, (224, 224))
            
            # 2. Denoising (bilateral filter on 224x224 is extremely fast!)
            denoised = cv2.bilateralFilter(img_resized, d=5, sigmaColor=50, sigmaSpace=50)
            
            # 3. CLAHE contrast enhancement
            lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l)
            lab_enhanced = cv2.merge((l_enhanced, a, b))
            bgr_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
            
            # 4. Convert BGR to RGB
            rgb = cv2.cvtColor(bgr_enhanced, cv2.COLOR_BGR2RGB)
            
            # 5. Normalize
            img_float = rgb.astype(np.float32) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            img_normalized = (img_float - mean) / std
            
            # [H, W, C] -> [C, H, W]
            tensor = img_normalized.transpose((2, 0, 1))
            return torch.tensor(tensor), label
        except Exception as e:
            # Fallback in case of corrupted file, return first sample
            print(f"Error loading image {img_path}: {e}. Returning first sample as fallback.")
            return self.__getitem__(0)

def train_herb_dataset(data_path: str, epochs: int = 5, batch_size: int = 32,
                        learning_rate: float = 0.001, save_path: str = None,
                        max_samples: int = 50):
    if save_path is None:
        save_path = str(project_root / "weights" / "herb_model.pth")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    # Build dataset and dataloader
    dataset = HerbLeafDataset(data_path, max_samples_per_class=max_samples)
    
    # Save classes to models/herb_classes.txt for the API server
    classes_dir = project_root / "models"
    classes_dir.mkdir(parents=True, exist_ok=True)
    classes_file = classes_dir / "herb_classes.txt"
    with open(classes_file, "w", encoding="utf-8") as f:
        f.write("\n".join(dataset.classes))
    print(f"Saved herb class names list ({len(dataset.classes)} classes) to {classes_file}")

    # Simple 80/20 split for train/val
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = torch.utils.data.random_split(dataset, [train_size, val_size])
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=0) # num_workers=0 safe on Windows
    val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False, num_workers=0)

    num_classes = len(dataset.classes)
    model = HerbClassifier(num_classes=num_classes, use_pretrained=True).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
        
        train_acc = 100. * correct / total
        avg_loss = running_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{epochs}] - Loss: {avg_loss:.4f} - Train Acc: {train_acc:.2f}%")

        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                _, predicted = outputs.max(1)
                val_total += targets.size(0)
                val_correct += predicted.eq(targets).sum().item()
        val_acc = 100. * val_correct / val_total if val_total > 0 else 0
        print(f"Validation Acc: {val_acc:.2f}%")

    # Ensure the weights directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"Herb model saved to {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train HerbClassifier on a real leaf dataset")
    parser.add_argument("--data-path", type=str, required=False, 
                        default=r"D:\XboxGames\MED117_Medicinal Plant Leaf Dataset & Name Table\MED117_Medicinal Plant Leaf Dataset & Name Table\MED 117 Leaf Species", 
                        help="Root directory of the leaf dataset")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--save-path", type=str, default=str(project_root / "weights" / "herb_model.pth"))
    parser.add_argument("--max-samples", type=int, default=50, help="Max image files per class (to run fast on CPU)")
    args = parser.parse_args()
    
    train_herb_dataset(
        data_path=args.data_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        save_path=args.save_path,
        max_samples=args.max_samples
    )
