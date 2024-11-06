import os
from typing import Tuple
import logging
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms


def preprocess_image(
    img_in: np.ndarray,
) -> Tuple[torch.Tensor, Tuple[int, int], Image.Image]:
    """
    Preprocess the input image without changing its resolution.

    Args:
        img_in (np.ndarray): The input image as a numpy array.

    Returns:
        Tuple[torch.Tensor, Tuple[int, int], Image.Image]:
            - The preprocessed image tensor ready for the model.
            - The original image size (width, height).
            - The original image as a PIL Image.
    """
    img_pil = Image.fromarray(img_in)

    original_size = img_pil.size  # (width, height)

    transform = transforms.Compose(
        [
            transforms.Resize((320, 320)),  # Keep 320x320 for the model
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    image_resized = transform(img_pil).unsqueeze(0)  # Add batch dimension

    return image_resized, original_size, img_pil


def salient_object_detection(
    model: torch.nn.Module, image_tensor: torch.Tensor
) -> np.ndarray:
    """
    Process the image tensor with the U2NET model to get the saliency map.

    Args:
        model (torch.nn.Module): The pre-trained U2NET model.
        image_tensor (torch.Tensor): The preprocessed image tensor.

    Returns:
        np.ndarray: The predicted saliency map as a numpy array.
    """
    with torch.no_grad():
        d1, _, _, _, _, _, _ = model(image_tensor)
        pred = d1[:, 0, :, :]
        # Upsample the prediction to 320x320 if necessary
        pred = F.interpolate(
            pred.unsqueeze(0), size=(320, 320), mode="bilinear", align_corners=False
        )
        pred = pred.squeeze().cpu().numpy()
        pred = (pred - np.min(pred)) / (np.max(pred) - np.min(pred))  # Normalize

    return pred


def apply_mask(
    image: Image.Image, mask: np.ndarray, original_size: Tuple[int, int]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Resize the mask to the original image size and apply it to the image.

    Args:
        image (Image.Image): The original image.
        mask (np.ndarray): The saliency mask.
        original_size (Tuple[int, int]): The original image size (width, height).

    Returns:
        Tuple[np.ndarray, np.ndarray]:
            A tuple containing:
            - The result image with the mask applied (np.ndarray).
            - The mask resized to the original image dimensions (np.ndarray).
    """
    # Resize the mask to the original image size
    mask_resized = cv2.resize(mask, original_size)
    mask_resized = np.expand_dims(mask_resized, axis=2)  # Shape (height, width, 1)

    # Convert image to numpy array
    image_np = np.array(image)  # Shape (height, width, 3)

    # Apply the mask
    image_np = (image_np * mask_resized).astype(np.uint8)

    # Change background to white
    # Convert mask to 0-255 uint8
    mask_uint8 = (mask_resized * 255).astype(np.uint8)

    # Create a boolean mask where mask is zero
    background_mask = mask_uint8.squeeze() == 0  # Shape (height, width)
    image_np[background_mask] = 255

    return image_np, mask_uint8
