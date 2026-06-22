import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

# We use a zero-shot classification model
# This model can classify text into categories WITHOUT being trained on them
# We just tell it the categories and it figures it out
HF_MODEL = "facebook/bart-large-mnli"

def validate_justification(justification: str, scheme_name: str) -> dict:
    """
    Uses Hugging Face zero-shot classification to check if the justification
    is specific and valid.
    
    What is zero-shot classification?
    Normal AI models need examples to learn categories.
    Zero-shot models are smart enough to classify text into NEW categories
    they've never seen before — just by understanding language.
    
    We give it two labels:
    - "specific and detailed justification" 
    - "vague and insufficient justification"
    
    The model reads the text and decides which label fits better.
    
    Why does this matter for government?
    Departments shouldn't get budget just by saying "we need money".
    They need to explain WHY specifically. This AI enforces that automatically.
    """
    
    if not justification or len(justification.strip()) < 20:
        return {
            "is_valid": False,
            "confidence": 1.0,
            "reason": "Justification is too short. Please provide a detailed explanation."
        }
    
    if not HF_API_KEY:
        # If no API key, do basic length/keyword check as fallback
        return _basic_validation(justification, scheme_name)
    
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        
        payload = {
            "inputs": f"Budget request for {scheme_name}: {justification}",
            "parameters": {
                "candidate_labels": [
                    "specific and detailed justification with clear objectives",
                    "vague and insufficient justification without clear purpose"
                ]
            }
        }
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        result = response.json()
        
        # result looks like:
        # {
        #   "labels": ["specific...", "vague..."],
        #   "scores": [0.85, 0.15]   <- confidence for each label
        # }
        
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        is_valid = "specific" in top_label
        
        return {
            "is_valid": is_valid,
            "confidence": round(top_score, 2),
            "reason": (
                "Justification is specific and acceptable." 
                if is_valid 
                else f"Justification appears vague (confidence: {round(top_score*100)}%). Please provide more specific details about how funds will be used."
            )
        }
        
    except Exception as e:
        print(f"[Justification AI] Error: {e}, using basic validation")
        return _basic_validation(justification, scheme_name)


def _basic_validation(justification: str, scheme_name: str) -> dict:
    """
    Fallback if Hugging Face is unavailable.
    Checks for basic quality signals in the justification text.
    """
    text = justification.lower()
    
    # Good justifications mention numbers, locations, or specific actions
    good_signals = [
        any(char.isdigit() for char in text),          # contains numbers
        any(word in text for word in [
            "district", "village", "ward", "block",
            "expand", "construct", "repair", "install",
            "beneficiar", "household", "patient", "student"
        ]),
        len(justification.split()) >= 10               # at least 10 words
    ]
    
    score = sum(good_signals)
    
    if score >= 2:
        return {
            "is_valid": True,
            "confidence": 0.75,
            "reason": "Justification meets basic requirements."
        }
    else:
        return {
            "is_valid": False,
            "confidence": 0.75,
            "reason": "Justification needs more detail — include specific locations, numbers, or objectives."
        }