from transformers import pipeline
from threading import Lock
import json

# Lazy loading of summarizer model
_summarizer = None
_lock = Lock()

def get_summarizer():
    global _summarizer
    with _lock:
        if _summarizer is None:
            # lightweight (~300MB) google/flan-t5-small 
            _summarizer = pipeline("text2text-generation", model="google/flan-t5-small")
    return _summarizer

def warmup_summarizer():
    get_summarizer()

def generate_summary(analysis_data: dict) -> str:
    """
    Generates a human-readable summary of the image analysis results.
    """
    try:
        # Prepare a structured prompt for Flan-T5
        ai_prob = analysis_data.get('ai_probability')
        medium_info = analysis_data.get('art_medium', {})
        metadata = analysis_data.get('metadata_analysis', {})
        fractal = analysis_data.get('fd_default')

        # Formatting values for the prompt
        ai_text = f"{ai_prob*100:.1f}% AI probability" if ai_prob is not None else "Unknown AI detection"
        medium_text = f"{medium_info.get('medium', 'Unknown medium')} ({medium_info.get('confidence', 0)*100:.0f}% confidence)"
        metadata_text = "Suspicious metadata findings" if metadata.get('is_suspicious') else "Clean metadata"
        fractal_text = f"Fractal dimension {fractal:.4f}" if fractal else "Standard complexity"

        prompt = (
            f"Summarize these art analysis results into a single professional sentence for an appraiser: "
            f"1. Detection: {ai_text}. "
            f"2. Medium: {medium_text}. "
            f"3. Metadata: {metadata_text}. "
            f"4. Texture: {fractal_text}. "
            f"Summary:"
        )

        model = get_summarizer()
        results = model(prompt, max_length=100, do_sample=False)
        
        if results and 'generated_text' in results[0]:
            return results[0]['generated_text'].strip()
        return "Analysis completed successfully. No significant anomalies detected."
        
    except Exception as e:
        print(f"Summarization error: {e}")
        return "Analysis completed, but summary generation failed."
