import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from models.classifiers import SkinConditionClassifier, HerbClassifier

# Ensure weights folder exists
os.makedirs("weights", exist_ok=True)
os.makedirs("temp_dataset", exist_ok=True)

# Class mappings
SKIN_CLASSES = ["Acne", "Eczema", "Pigmentation", "Dry Skin", "Wrinkles", "Psoriasis", "Rosacea", "Healthy Skin"]
HERB_CLASSES = [
    "Neem", "Aloe Vera", "Turmeric", "Tulsi", "Amla", 
    "Harra", "Bahera", "Giloy", "Mahua", "Karanj", 
    "Palash", "Moringa", "Hibiscus", "Ashwagandha", 
    "Bael", "Arjun", "Chironji", "Bhringraj"
]

class SyntheticDataset(Dataset):
    def __init__(self, data_type="skin", num_samples_per_class=30):
        self.data_type = data_type
        self.samples = []
        self.labels = []
        self.classes = SKIN_CLASSES if data_type == "skin" else HERB_CLASSES
        
        self.generate_data(num_samples_per_class)

    def generate_data(self, num_samples_per_class):
        for class_idx, class_name in enumerate(self.classes):
            for s in range(num_samples_per_class):
                # Create a blank image 224x224x3
                img = np.zeros((224, 224, 3), dtype=np.uint8)
                
                if self.data_type == "skin":
                    # Base skin color (warm beige tone)
                    img[:, :] = [140, 180, 240] # BGR format (R=240, G=180, B=140)
                    
                    if class_name == "Acne":
                        # Draw red circles with white heads (acne spots)
                        for _ in range(5):
                            cx, cy = np.random.randint(40, 184, 2)
                            r = np.random.randint(4, 10)
                            cv2.circle(img, (cx, cy), r, (50, 50, 220), -1) # Red spot
                            cv2.circle(img, (cx, cy), r // 2, (200, 240, 240), -1) # White center
                    elif class_name == "Eczema":
                        # Draw irregular red, dry patches
                        for _ in range(3):
                            cx, cy = np.random.randint(60, 160, 2)
                            r = np.random.randint(15, 30)
                            cv2.circle(img, (cx, cy), r, (100, 110, 200), -1) # Dry reddish patch
                            # Add some texture noise inside patch
                            for _ in range(10):
                                nx = cx + np.random.randint(-r, r)
                                ny = cy + np.random.randint(-r, r)
                                cv2.circle(img, (nx, ny), 2, (150, 180, 210), -1)
                    elif class_name == "Pigmentation":
                        # Draw smooth darker brown patches (ellipses)
                        for _ in range(2):
                            cx, cy = np.random.randint(60, 160, 2)
                            ax1, ax2 = np.random.randint(15, 35, 2)
                            angle = np.random.randint(0, 180)
                            cv2.ellipse(img, (cx, cy), (ax1, ax2), angle, 0, 360, (70, 100, 150), -1) # Brown spot
                    elif class_name == "Dry Skin":
                        # Draw white scaly lines representing peeling skin
                        for _ in range(15):
                            x1, y1 = np.random.randint(30, 194, 2)
                            x2 = x1 + np.random.randint(-15, 15)
                            y2 = y1 + np.random.randint(-15, 15)
                            cv2.line(img, (x1, y1), (x2, y2), (220, 230, 230), 1)
                    elif class_name == "Wrinkles":
                        # Draw thin dark curved lines
                        for _ in range(6):
                            points = []
                            start_x = np.random.randint(30, 80)
                            start_y = np.random.randint(40, 180)
                            for i in range(5):
                                points.append([start_x + i * 25, start_y + int(10 * np.sin(i)) + np.random.randint(-3, 3)])
                            pts = np.array(points, np.int32).reshape((-1, 1, 2))
                            cv2.polylines(img, [pts], False, (100, 120, 130), 1)
                    elif class_name == "Psoriasis":
                        # Silvery white scales on red plaques
                        for _ in range(3):
                            cx, cy = np.random.randint(60, 160, 2)
                            r = np.random.randint(20, 35)
                            cv2.circle(img, (cx, cy), r, (80, 90, 190), -1) # Red plaque
                            cv2.circle(img, (cx, cy), r - 5, (220, 225, 225), -1) # Silvery scale center
                    elif class_name == "Rosacea":
                        # Diffuse red flushing with tiny capillary lines
                        for _ in range(30):
                            cx, cy = np.random.randint(20, 204, 2)
                            cv2.circle(img, (cx, cy), np.random.randint(10, 25), (130, 140, 235), -1) # Mild flush
                        for _ in range(8):
                            x1, y1 = np.random.randint(40, 184, 2)
                            x2 = x1 + np.random.randint(-8, 8)
                            y2 = y1 + np.random.randint(-8, 8)
                            cv2.line(img, (x1, y1), (x2, y2), (60, 60, 200), 1) # Capillaries
                    elif class_name == "Healthy Skin":
                        # Smooth skin, add light gaussian noise to simulate natural texture
                        noise = np.random.normal(0, 3, img.shape).astype(np.int16)
                        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
                        
                else: # Herbal leaf generation
                    # Base black/dark soil background
                    img[:, :] = [30, 40, 35]
                    
                    # Draw a stem
                    cv2.line(img, (112, 220), (112, 60), (35, 75, 90), 4)
                    
                    # Depending on class, draw leaves of different colors, counts, and sizes
                    # Let's map herb classes to distinct features to help training
                    seed = hash(class_name) % 100
                    leaf_color = (40 + (seed % 4) * 30, 150 + (seed % 3) * 30, 50 + (seed % 5) * 20) # Various green hues
                    
                    if class_name in ["Neem", "Tulsi", "Bhringraj"]:
                        # Pointed small leaves (serrated/multiple)
                        # Draw 3-5 leaflets pointing outwards
                        for offset_y in [80, 120, 160]:
                            cv2.ellipse(img, (112 - 25, offset_y), (25, 10), -20, 0, 360, leaf_color, -1)
                            cv2.ellipse(img, (112 + 25, offset_y), (25, 10), 20, 0, 360, leaf_color, -1)
                    elif class_name in ["Aloe Vera", "Giloy"]:
                        # Long thick succulent spear/heart leaves
                        if class_name == "Aloe Vera":
                            # Tall triangular spear pointing up
                            points = np.array([[112, 30], [80, 200], [144, 200]], np.int32)
                            cv2.drawContours(img, [points], 0, leaf_color, -1)
                            # Add small white spike dots
                            for spike_y in range(50, 190, 20):
                                cv2.circle(img, (112 - 12, spike_y), 2, (200, 255, 255), -1)
                                cv2.circle(img, (112 + 12, spike_y), 2, (200, 255, 255), -1)
                        else: # Giloy (heart shape)
                            cv2.ellipse(img, (100, 112), (30, 30), 0, 0, 360, leaf_color, -1)
                            cv2.ellipse(img, (124, 112), (30, 30), 0, 0, 360, leaf_color, -1)
                            points = np.array([[70, 112], [154, 112], [112, 170]], np.int32)
                            cv2.drawContours(img, [points], 0, leaf_color, -1)
                    else:
                        # Standard single large leaf
                        # Ellipse in center
                        axes_w = 30 + (seed % 4) * 8
                        axes_h = 50 + (seed % 3) * 12
                        angle = -15 if (seed % 2 == 0) else 15
                        cv2.ellipse(img, (112, 112), (axes_w, axes_h), angle, 0, 360, leaf_color, -1)
                        # Add a tip
                        cv2.circle(img, (112, 112 - axes_h + 5), 8, leaf_color, -1)
                        
                # Preprocess data to match input pipeline requirements
                # Convert BGR to RGB
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # Normalize float values
                img_float = rgb.astype(np.float32) / 255.0
                mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
                std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
                img_normalized = (img_float - mean) / std
                # [H, W, C] -> [C, H, W]
                tensor = img_normalized.transpose((2, 0, 1))
                
                self.samples.append(torch.tensor(tensor))
                self.labels.append(class_idx)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx], self.labels[idx]

def train_model(data_type="skin", epochs=3, num_classes=8):
    print(f"Generating synthetic training dataset for {data_type} classification...")
    dataset = SyntheticDataset(data_type=data_type, num_samples_per_class=20)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
    
    print(f"Initializing {data_type} classification model (using lightweight settings)...")
    if data_type == "skin":
        model = SkinConditionClassifier(num_classes=num_classes, use_pretrained=False)
    else:
        model = HerbClassifier(num_classes=num_classes, use_pretrained=False)
        
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    model.train()
    print(f"Starting training loop ({epochs} epochs)...")
    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        for i, (inputs, targets) in enumerate(dataloader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
        acc = 100. * correct / total
        print(f"Epoch [{epoch+1}/{epochs}] - Loss: {running_loss/len(dataloader):.4f} - Acc: {acc:.2f}%")
        
    # Save the model state dict
    weights_path = f"weights/{data_type}_model.pth"
    torch.save(model.state_dict(), weights_path)
    print(f"Model saved successfully to {weights_path}")
    print("-" * 50)

if __name__ == "__main__":
    print("Initializing synthetic Ayurvedic AI model training script...")
    # Train skin classifier (8 classes)
    train_model(data_type="skin", epochs=3, num_classes=len(SKIN_CLASSES))
    # Train herb classifier (18 classes)
    train_model(data_type="herb", epochs=3, num_classes=len(HERB_CLASSES))
    print("AI Model weights pre-trained and saved successfully!")
