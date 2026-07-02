import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import logging

logger = logging.getLogger(__name__)

class CustomCNN(nn.Module):
    """
    A lightweight custom CNN that serves as a fallback or primary architecture.
    Ensures that offline systems or restricted environments do not fail during loading.
    """
    def __init__(self, num_classes):
        super(CustomCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # 112
            
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # 56
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # 28
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # 14
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((7, 7)),
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

class SkinConditionClassifier(nn.Module):
    def __init__(self, num_classes=8, use_pretrained=True):
        super(SkinConditionClassifier, self).__init__()
        self.num_classes = num_classes
        try:
            # Try to load MobileNetV3 small
            weights = models.MobileNet_V3_Small_Weights.DEFAULT if use_pretrained else None
            self.model = models.mobilenet_v3_small(weights=weights)
            # Re-define the classifier head
            in_features = self.model.classifier[0].in_features
            self.model.classifier = nn.Sequential(
                nn.Linear(in_features, 1024),
                nn.Hardswish(),
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(1024, num_classes)
            )
            self.is_custom = False
            logger.info("Loaded MobileNetV3 for SkinConditionClassifier")
        except Exception as e:
            logger.warning(f"Failed to load pre-trained MobileNetV3: {e}. Falling back to CustomCNN.")
            self.model = CustomCNN(num_classes)
            self.is_custom = True

    def forward(self, x):
        return self.model(x)

    def get_last_conv_layer(self):
        """
        Returns the last convolutional layer, necessary for Grad-CAM.
        """
        if self.is_custom:
            return self.model.features[-4] # The last Conv2d layer
        else:
            return self.model.features[-1] # MobileNetV3 last feature block Conv2d

class HerbClassifier(nn.Module):
    def __init__(self, num_classes=18, use_pretrained=True):
        super(HerbClassifier, self).__init__()
        self.num_classes = num_classes
        try:
            # Try to load MobileNetV3 small
            weights = models.MobileNet_V3_Small_Weights.DEFAULT if use_pretrained else None
            self.model = models.mobilenet_v3_small(weights=weights)
            # Re-define the classifier head
            in_features = self.model.classifier[0].in_features
            self.model.classifier = nn.Sequential(
                nn.Linear(in_features, 1024),
                nn.Hardswish(),
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(1024, num_classes)
            )
            self.is_custom = False
            logger.info("Loaded MobileNetV3 for HerbClassifier")
        except Exception as e:
            logger.warning(f"Failed to load pre-trained MobileNetV3: {e}. Falling back to CustomCNN.")
            self.model = CustomCNN(num_classes)
            self.is_custom = True

    def forward(self, x):
        return self.model(x)

    def get_last_conv_layer(self):
        if self.is_custom:
            return self.model.features[-4]
        else:
            return self.model.features[-1]
