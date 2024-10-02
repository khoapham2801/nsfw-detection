from io import BytesIO

import imagehash
from fastapi import FastAPI, File, UploadFile
from loguru import logger
import os

# Load model directly
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer_provider, set_tracer_provider

set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "nsfw-det-app-tracing"}))
)
tracer = get_tracer_provider().get_tracer("myocr", "0.1.2")
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("processors") as processors:
    with tracer.start_as_current_span(
            "model-loader", links=[trace.Link(processors.get_span_context())]
        ):
        os.makedirs("./model_cache", exist_ok=True)
        processor = AutoImageProcessor.from_pretrained("Falconsai/nsfw_image_detection", cache_dir = "./model_cache")
        model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection", cache_dir = "./model_cache")
        if torch.cuda.is_available():
            device = torch.device("cuda:0")
            logger.info(f"Device: cuda-0")
        else:
            device = torch.device("cpu")
            logger.info(f"Device: cpu")
        model = model.to(device)

    # main logic
    cache = {}

    app = FastAPI(root_path="/")

    @app.post("/nsfw_detection")
    async def nsfw_detection(file: UploadFile = File(...)):
        with tracer.start_as_current_span(
            "read-image", links=[trace.Link(processors.get_span_context())]
        ):
            request_object_content = await file.read()
            image = Image.open(BytesIO(request_object_content)).convert("RGB")
            image_hash = imagehash.average_hash(image)

        if image_hash not in cache:
            with tracer.start_as_current_span(
                "process-image", links=[trace.Link(processors.get_span_context())]
            ):
                logger.info("Processing image...")
                inputs = processor(images=image, return_tensors="pt")
                inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with tracer.start_as_current_span(
                "inference", links=[trace.Link(processors.get_span_context())]
            ):
                logger.info("Inferencing...")
                with torch.no_grad():
                    logits = model(**inputs).logits
                scores = logits.tolist()
                cache[image_hash] = scores
        else:
           with tracer.start_as_current_span(
                "retrieval", links=[trace.Link(processors.get_span_context())]
            ):
                logger.info("Retrieving detection result from history!")
                scores = cache[image_hash]

        predicted_label = scores.index(max(scores))
        result = model.config.id2label[predicted_label]
        logger.info("Detection DONE!")
        return result, scores