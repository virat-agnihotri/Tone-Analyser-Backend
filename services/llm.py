import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from config import LLM_MODEL, get_hf_token

_tokenizer = None
_model = None


import os

def get_llm_model():
    global _tokenizer, _model
    if _model is None or _tokenizer is None:
        print(f"Loading Hugging Face LLM model: {LLM_MODEL}")
        is_offline = os.getenv("HF_HUB_OFFLINE", "0") in ("1", "true", "True")

        try:
            _tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL, local_files_only=True)
            _model = AutoModelForSeq2SeqLM.from_pretrained(
                LLM_MODEL,
                dtype=torch.float32,
                local_files_only=True
            )
            _model.eval()
            print(f"Loaded LLM model '{LLM_MODEL}' from local cache.")
            return _tokenizer, _model
        except Exception as local_err:
            if is_offline:
                print(
                    "Unable to reach Hugging Face Hub.\n"
                    "This may be a DNS/network problem rather than an authentication problem.\n"
                    "Please verify that huggingface.co can be resolved and reached."
                )
                raise RuntimeError(
                    f"LLM model '{LLM_MODEL}' is not available in local cache and offline mode is active."
                ) from local_err
            print(f"LLM model '{LLM_MODEL}' not cached. Trying online load...")

        try:
            _tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL, local_files_only=False)
            _model = AutoModelForSeq2SeqLM.from_pretrained(
                LLM_MODEL,
                dtype=torch.float32,
                local_files_only=False
            )
            _model.eval()
            print(f"Successfully downloaded and loaded LLM model '{LLM_MODEL}'.")
        except Exception as net_err:
            print(
                "Unable to reach Hugging Face Hub.\n"
                "This may be a DNS/network problem rather than an authentication problem.\n"
                "Please verify that huggingface.co can be resolved and reached."
            )
            raise RuntimeError(
                f"LLM model '{LLM_MODEL}' is not cached and Hugging Face (huggingface.co) "
                f"could not be reached: {net_err}"
            ) from net_err

    return _tokenizer, _model


def generate_insights(
    transcript: str,
    stress: dict,
    emotion: dict,
    lap_data: dict,
    context: list[str]
) -> str:
    stress_score = stress.get("score", 0.0) if stress else 0.0
    stress_level = stress.get("level", "Low") if stress else "Low"
    emotion_name = emotion.get("emotion", "neutral") if emotion else "neutral"
    knowledge_str = "; ".join(context) if context else "Standard racing protocol."
    obs_list = lap_data.get("observations", []) if isinstance(lap_data, dict) else []

    prompt = (
        f"Synthesize driver racing briefing insight:\n"
        f"Driver speech: '{transcript}'\n"
        f"Emotion: {emotion_name}. Stress: {stress_score}/100 ({stress_level}).\n"
        f"Racing protocol: {knowledge_str}\n"
        f"Telemetry: {obs_list}\n"
        f"Briefing summary:"
    )

    try:
        tokenizer, model = get_llm_model()
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=120,
                do_sample=False,
                num_beams=2,
                early_stopping=True
            )
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        if generated_text:
            return (
                f"Hugging Face AI Analysis ({LLM_MODEL}): {generated_text} "
                f"[Driver State: {emotion_name.capitalize()} | Stress Index: {stress_score}/100 ({stress_level})]"
            )
    except Exception as e:
        print(f"Warning: HF LLM generation error ({e}). Returning fallback insight.")

    return (
        f"Driver exhibited {emotion_name} vocal tone with an estimated stress score of {stress_score}/100 ({stress_level} level). "
        f"Acoustic telemetry factors: {', '.join(stress.get('factors', [])) if stress else 'N/A'}. "
        f"RAG Knowledge Context: {knowledge_str}"
    )


def generate_recommendations(insights: str) -> list[str]:
    prompt = (
        f"Based on driver analysis: {insights}\n"
        f"List 3 short actionable coaching recommendations:"
    )

    try:
        tokenizer, model = get_llm_model()
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=80,
                do_sample=False,
                num_beams=2,
                early_stopping=True
            )
        text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        lines = [line.strip("- •123456789. ") for line in text.splitlines() if line.strip()]
        if len(lines) >= 3:
            return lines[:3]
        elif text:
            return [text, "Maintain smooth braking inputs.", "Regulate breathing during safety car laps."]
    except Exception as e:
        print(f"Warning: HF LLM recommendation error ({e}). Returning fallback recommendations.")

    return [
        "Maintain calm radio communications during intense cornering.",
        "Focus on smooth trail braking to maintain minimum apex speed.",
        "Regulate breathing during safety car laps to keep vocal pitch stable."
    ]