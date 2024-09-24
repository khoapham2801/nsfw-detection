from io import BytesIO

import imagehash
from fastapi import FastAPI, File, UploadFile
from loguru import logger
import os

# Load model directly
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch

os.makedirs("./model_cache", exist_ok=True)
processor = AutoImageProcessor.from_pretrained("Falconsai/nsfw_image_detection", cache_dir = "./model_cache")
model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection", cache_dir = "./model_cache")

if torch.cuda.is_available():
    device = torch.device("cuda")
    logger.info(f"Device: cuda")
else:
    device = torch.device("cpu")
    logger.info(f"Device: cpu")
model = model.to(device)

# main logic
cache = {}

app = FastAPI(root_path="/")

@app.post("/nsfw_detection")
async def nsfw_detection(file: UploadFile = File(...)):
    request_object_content = await file.read()
    image = Image.open(BytesIO(request_object_content)).convert("RGB")
    image_hash = imagehash.average_hash(image)

    if image_hash not in cache:
        inputs = processor(images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = model(**inputs).logits
        scores = logits.tolist()
        cache[image_hash] = scores
    else:
        scores = cache[image_hash]

    predicted_label = scores.index(max(scores))
    result = model.config.id2label[predicted_label]
    return result, scores