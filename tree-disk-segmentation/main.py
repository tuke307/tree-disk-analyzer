import argparse
import os
from typing import Tuple
import logging
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from src.u2net import U2NET


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def load_model(model_path: str) -> torch.nn.Module:
    """
    Load the pre-trained U2NET model.

    Args:
        model_path (str): Path to the pre-trained model weights.

    Returns:
        torch.nn.Module: The loaded U2NET model in evaluation mode.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model weights file '{model_path}' not found.")

    model = U2NET()
    state_dict = torch.load(
        model_path, map_location=torch.device("cpu"), weights_only=True
    )
    model.load_state_dict(state_dict)
    model.eval()
    return model


def preprocess_image(
    image_path: str,
) -> Tuple[torch.Tensor, Tuple[int, int], Image.Image]:
    """
    Preprocess the input image without changing its resolution.

    Args:
        image_path (str): Path to the input image.

    Returns:
        Tuple[torch.Tensor, Tuple[int, int], Image.Image]:
            - The preprocessed image tensor ready for the model.
            - The original image size (width, height).
            - The original image as a PIL Image.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image file '{image_path}' not found.")

    image = Image.open(image_path).convert("RGB")
    original_size = image.size  # (width, height)
    transform = transforms.Compose(
        [
            transforms.Resize((320, 320)),  # Keep 320x320 for the model
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    image_resized = transform(image).unsqueeze(0)  # Add batch dimension
    return image_resized, original_size, image


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
            - The result image with the mask applied.
            - The mask resized to the original image dimensions.
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


def save_image(output_path: str, result_image: np.ndarray) -> None:
    """
    Save the final image after removing the salient object.

    Args:
        output_path (str): Path to save the output image.
        result_image (np.ndarray): The result image with the background set to white.

    Returns:
        None
    """
    # Convert to BGR if needed
    result_image_bgr = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, result_image_bgr)


def remove_salient_object(
    image_path: str,
    output_path: str,
    model_path: str,
) -> np.ndarray:
    """
    Pipeline to remove the salient object while maintaining the original resolution.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the output image.
        model_path (str): Path to the pre-trained model weights.

    Returns:
        np.ndarray: The mask resized to the original image dimensions.
    """
    model = load_model(model_path)
    image_tensor, original_size, original_image = preprocess_image(image_path)
    mask = salient_object_detection(model, image_tensor)
    result_image, mask_original_dim = apply_mask(original_image, mask, original_size)
    save_image(output_path, result_image)
    return mask_original_dim


def main(
    input_image_path: str,
    output_image_path: str,
    model_path: str,
) -> None:
    """
    Main function to remove the salient object from an image.

    Args:
        input_image_path (str): Path to the input image.
        output_image_path (str): Path to save the output image.
        model_path (str): Path to the pre-trained model weights.

    Returns:
        None
    """
    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input image file '{input_image_path}' not found.")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model weights file '{model_path}' not found.")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_image_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    remove_salient_object(input_image_path, output_image_path, model_path)
    logger.info(f"Salient object removed. Output saved to '{output_image_path}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove salient object from image")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input image",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to save the output image",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="./models/segmentation/u2net.pth",
        help="Path to the model weights",
    )
    args = parser.parse_args()

    main(args.input, args.output, args.model)
