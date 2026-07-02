import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self.forward_hook = self.target_layer.register_forward_hook(self.save_activation)
        self.backward_hook = self.target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output.detach()

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate_heatmap(self, input_tensor, class_idx=None):
        self.model.eval()
        output = self.model(input_tensor)
        
        if class_idx is None:
            class_idx = torch.argmax(output, dim=1).item()
            
        self.model.zero_grad()
        score = output[0, class_idx]
        score.backward()
        
        # Get gradients and activations
        gradients = self.gradients[0] # [C, H, W]
        activations = self.activations[0] # [C, H, W]
        
        # Global average pooling of gradients
        weights = torch.mean(gradients, dim=(1, 2), keepdim=True) # [C, 1, 1]
        
        # Weighted sum of activations
        cam = torch.sum(weights * activations, dim=0) # [H, W]
        
        # Apply ReLU to keep positive activations
        cam = torch.clamp(cam, min=0)
        
        # Normalize between 0 and 1
        cam_np = cam.cpu().numpy()
        if np.max(cam_np) > 0:
            cam_np = cam_np / np.max(cam_np)
            
        return cam_np, class_idx

    def overlay_heatmap(self, heatmap, original_image, alpha=0.5, colormap=cv2.COLORMAP_JET):
        """
        Overlays heatmap on original image.
        original_image: numpy array (H, W, 3) in BGR or RGB.
        heatmap: numpy array (H, W) normalized between 0 and 1.
        """
        # Resize heatmap to match original image size
        heatmap_resized = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))
        
        # Convert to 0-255 range
        heatmap_color = np.uint8(255 * heatmap_resized)
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap_color, colormap)
        
        # Blend original image and colored heatmap
        blended = cv2.addWeighted(original_image, 1 - alpha, heatmap_colored, alpha, 0)
        return blended

    def remove_hooks(self):
        self.forward_hook.remove()
        self.backward_hook.remove()
        
    def __del__(self):
        try:
            self.remove_hooks()
        except:
            pass
