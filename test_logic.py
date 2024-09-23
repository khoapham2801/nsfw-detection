from io import BytesIO

import imagehash
from loguru import logger
import os

# Load model directly
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch

def test_model():
    os.makedirs("./model_cache")
    processor = AutoImageProcessor.from_pretrained("Falconsai/nsfw_image_detection", cache_dir = "./model_cache")
    model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection", cache_dir = "./model_cache")
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    model = model.to(device)

    image = Image.open("test.png").convert("RGB")

    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits
    scores = logits.tolist()
    predicted_label = logits.argmax(-1).item()
    result = model.config.id2label[predicted_label]
    assert result == "normal"



