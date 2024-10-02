# Read more about OpenTelemetry here:
# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html
from io import BytesIO

import imagehash
from fastapi import FastAPI, File, UploadFile
from loguru import logger
import os
from time import time

# Load model directly
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch

from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from prometheus_client import start_http_server

# Start Prometheus client
start_http_server(port=8099, addr="0.0.0.0")

# Service name is required for most backends
resource = Resource(attributes={SERVICE_NAME: "nsfw-det-service"})

# Exporter to export metrics to Prometheus
reader = PrometheusMetricReader()

# Meter is responsible for creating and recording metrics
provider = MeterProvider(resource=resource, metric_readers=[reader])
set_meter_provider(provider)
meter = metrics.get_meter("nsfw_det", "0.1.2")

# Create your first counter
counter = meter.create_counter(
    name="nsfw_det_request_counter",
    description="Number of detection requests"
)

histogram = meter.create_histogram(
    name="nsfw_det_response_histogram",
    description="Detection response histogram",
    unit="seconds",
)


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

app = FastAPI()

@app.post("/nsfw_detection")
async def nsfw_detection(file: UploadFile = File(...)):
    # Mark the starting point for the response
    starting_time = time()

    request_object_content = await file.read()
    image = Image.open(BytesIO(request_object_content)).convert("RGB")
    image_hash = imagehash.average_hash(image)

    if image_hash not in cache:
        logger.info("Processing image...")
        inputs = processor(images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        logger.info("Inferencing...")
        with torch.no_grad():
            logits = model(**inputs).logits
        scores = logits.tolist()
        cache[image_hash] = scores
    else:
        logger.info("Retrieving detection result from history!")
        scores = cache[image_hash]

    predicted_label = scores.index(max(scores))
    result = model.config.id2label[predicted_label]
    logger.info("Detection DONE!")

    # Labels for all metrics
    label = {"api": "/nsfw_detection"}

    # Increase the counter
    counter.add(10, label)

    # Mark the end of the response
    ending_time = time()
    elapsed_time = ending_time - starting_time

    # Add histogram
    logger.info("elapsed time: ", elapsed_time)
    logger.info(elapsed_time)
    histogram.record(elapsed_time, label)

    return result, scores