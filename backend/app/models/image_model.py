import torch
import timm
from torchvision import transforms
from PIL import Image
from ultralytics import YOLO
from typing import Tuple
from backend.app.utils.mapping import CHEST_CLASSES,ALZHEIMER_CLASSES_CNN
from backend.app.config import MODEL_DIR
import numpy as np
import tensorflow as tf
from PIL import Image
from typing import Tuple
from backend.app.config import MODEL_DIR

def get_num_classes_from_checkpoint(state_dict, model_name: str) -> int:
    if "swin" in model_name.lower():
        if "head.fc.weight" in state_dict:
            return state_dict["head.fc.weight"].shape[0]
        if "head.weight" in state_dict:
            return state_dict["head.weight"].shape[0]
    else:
        if "classifier.weight" in state_dict:
            return state_dict["classifier.weight"].shape[0]
        if "head.fc.weight" in state_dict:
            return state_dict["head.fc.weight"].shape[0]
        if "head.weight" in state_dict:
            return state_dict["head.weight"].shape[0]

    for k, v in state_dict.items():
        if k.endswith(".weight") and len(v.shape) == 2:
            return v.shape[0]
    raise ValueError("Could not infer num classes")

# Tensorflow Architectured Chest Model
class TFChestModel:
    """Wrapper for TensorFlow chest X-ray model (Normal vs Pneumonia)."""
    def __init__(self, filename: str):
        model_path = MODEL_DIR / filename
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.model = tf.keras.models.load_model(model_path)
        # Keep labels lowercase to match CHEST_CLASSES
        self.class_names = ["normal", "pneumonia"]

    def preprocess(self, image_path: str):
        img = Image.open(image_path).convert("RGB").resize((224, 224))
        img_array = np.array(img) / 255.0
        return np.expand_dims(img_array, axis=0)

    def predict_from_path(self, image_path: str) -> Tuple[str, float]:
        arr = self.preprocess(image_path)
        prob = float(self.model.predict(arr)[0][0])
        if prob >= 0.5:
            return "pneumonia", prob
        else:
            return "normal", 1 - prob

class TFAlzheimerModel:
    """Wrapper for custom TensorFlow Alzheimer CNN model (.keras format)."""
    def __init__(self, filename: str):
        model_path = MODEL_DIR / filename
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        # load .keras model
        self.model = tf.keras.models.load_model(model_path)
        self.class_names = ALZHEIMER_CLASSES_CNN  # from utils/mapping.py

    def preprocess(self, image_path: str):
        img = Image.open(image_path).convert("L").resize((224, 224))  # grayscale
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=-1)  # add channel dimension
        return np.expand_dims(img_array, axis=0)

    def predict_from_path(self, image_path: str) -> Tuple[str, float]:
        arr = self.preprocess(image_path)
        probs = self.model.predict(arr)[0]
        top_idx = int(np.argmax(probs))
        conf = float(probs[top_idx])
        return self.class_names[top_idx], conf



class TimmChestModel:
    def __init__(self, filename: str, model_name: str, device=None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        model_path = MODEL_DIR / filename
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        checkpoint = torch.load(model_path, map_location=self.device)
        state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
        num_classes = get_num_classes_from_checkpoint(state_dict, model_name)

        self.class_names = CHEST_CLASSES[:num_classes]
        self.model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
        self.model.load_state_dict(state_dict, strict=False)
        self.model.to(self.device).eval()

        self.transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])

    def predict_from_path(self, image_path: str) -> Tuple[str, float]:
        img = Image.open(image_path).convert("RGB")
        x = self.transforms(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            outputs = self.model(x)
            probs = torch.softmax(outputs, dim=1)[0]
            top_idx = int(probs.argmax().item())
            conf = float(probs[top_idx].item())
            pred_class = self.class_names[top_idx]
        return pred_class, conf

class UltralyticsYOLOModel:
    def __init__(self, filename: str, class_names: list):
        model_path = MODEL_DIR / filename
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.model = YOLO(str(model_path))
        self.class_names = class_names

    def predict_from_path(self, image_path: str) -> Tuple[str, float]:
        results = self.model(image_path)
        r = results[0]
        if hasattr(r, "probs") and r.probs is not None:
            top_idx = int(r.probs.top1)
            conf = float(r.probs.data[top_idx].item())
            pred_name = r.names[top_idx] if hasattr(r, "names") else self.class_names[top_idx]
            return pred_name, conf
        return "unknown", 0.0
