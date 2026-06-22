import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

HF_IMAGE_MODEL = "openai/clip-vit-base-patch32"

COMPLAINT_CATEGORIES = [
    "road damage or pothole",
    "garbage or waste dumping",
    "flooding or waterlogging",
    "broken streetlight",
    "sewage overflow",
    "illegal construction",
    "water supply issue",
    "public property damage"
]

CATEGORY_TO_DEPARTMENT = {
    "road damage or pothole": "Infrastructure",
    "garbage or waste dumping": "Sanitation",
    "flooding or waterlogging": "Infrastructure",
    "broken streetlight": "Electricity",
    "sewage overflow": "Sanitation",
    "illegal construction": "Urban Development",
    "water supply issue": "Water Supply",
    "public property damage": "Municipal"
}


def classify_complaint_image(image_bytes: bytes) -> dict:
    """
    Sends an image to Hugging Face CLIP model and classifies
    what type of civic problem it shows.

    How CLIP works:
    CLIP (Contrastive Language-Image Pre-training) by OpenAI
    understands BOTH images and text. We give it:
    - An image (the complaint photo)
    - A list of text labels (our complaint categories)

    It figures out which text label best describes the image.
    This is called zero-shot classification — no training needed.

    Returns:
    - category: what type of problem it is
    - department: which dept should handle it
    - confidence: how sure the model is (0-1)
    - all_scores: scores for all categories
    """

    if not HF_API_KEY:
        return {
            "category": "public property damage",
            "department": "Municipal",
            "confidence": 0.0,
            "error": "No HF API key found"
        }

    try:
        # Convert image to base64 — this is how we send images over HTTP
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        headers = {"Authorization": f"Bearer {HF_API_KEY}"}

        payload = {
            "inputs": {
                "image": image_b64,
                "candidate_labels": COMPLAINT_CATEGORIES
            }
        }

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}",
            headers=headers,
            json=payload,
            timeout=15
        )

        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            # Find the highest scoring category
            top = max(result, key=lambda x: x["score"])
            category = top["label"]
            confidence = round(top["score"], 2)

            # If confidence is too low, fall back
            if confidence < 0.15:
                return _fallback_classification()

            department = CATEGORY_TO_DEPARTMENT.get(category, "Municipal")

            return {
                "category": category,
                "department": department,
                "confidence": confidence,
                "all_scores": {r["label"]: round(r["score"], 2) for r in result}
            }
        else:
            return _fallback_classification()

    except Exception as e:
        print(f"[Image Classifier] Error: {e}")
        return _fallback_classification()


def _fallback_classification() -> dict:
    return {
        "category": "public property damage",
        "department": "Municipal",
        "confidence": 0.0,
        "note": "Could not classify image, assigned to Municipal by default"
    }