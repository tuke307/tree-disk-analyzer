import os
import torch
from .u2net import U2NET


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
