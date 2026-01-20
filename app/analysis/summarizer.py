from transformers import pipeline
from threading import Lock
import json

SUMMARIZER_TEMPERATURE = 0.75

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
        medium_info = analysis_data.get('art_medium_analysis', {})
        metadata = analysis_data.get('metadata_analysis', {})
        fractal = analysis_data.get('fd_default')
        detections = analysis_data.get('object_detection', [])

        # Formatting values for the prompt
        ai_text = f"{ai_prob*100:.1f}% AI probability" if ai_prob is not None else "Unknown AI detection"
        medium_text = f"Medium is {medium_info.get('medium', 'Unknown')} ({medium_info.get('confidence', 0)*100:.0f}% confidence)"
        metadata_text = "Metadata is suspicious" if metadata.get('is_suspicious') else "Metadata is clean"
        fractal_text = f"Fractal dimension is {fractal:.4f}" if fractal else "Complexity is standard"
        
        det_text = ""
        if detections:
            labels = [d['label'] for d in detections]
            # Limit to top 3 labels to keep prompt short
            unique_labels = list(dict.fromkeys(labels))[:3]
            det_text = f"Detected objects: {', '.join(unique_labels)}."
        else:
            det_text = "No specific objects detected."

        # Simplified prompt for small models
        # The model has a 512-token limit (including input/output)
        prompt = (
            f"Compile Input into 3 long sentences as Output.\n"
            f"Input: 10% AI probability. Medium is Canvas. No specific objects. Metadata is clean. Complexity is standard.\n"
            f"Output: The image shows a low 10% AI probability and is identified as a canvas work with no suspicious objects found. The metadata is clean and the complexity is standard. These factors suggest the piece is likely authentic.\n"
            f"Input: {ai_text}. {medium_text}. {det_text} {metadata_text}. {fractal_text}.\n"
            f"Output:"
        )

        model = get_summarizer()
        # Adjusted parameters for flan-t5-small to reduce repetition and improve variety
        results = model(
            prompt, 
            max_new_tokens=120, 
            do_sample=True, 
            temperature=SUMMARIZER_TEMPERATURE, 
            top_p=0.9,
            repetition_penalty=1.5,
            no_repeat_ngram_size=3
        )
        
        # Logging raw performance to a specific file
        with open("/app/debug_summarizer.log", "a") as f:
            f.write(f"\n!!!! DEBUG SUMMARIZER START !!!!\n{results}\n!!!! DEBUG SUMMARIZER END !!!!\n")
            f.flush()

        if results and 'generated_text' in results[0]:
            summary = results[0]['generated_text'].strip()
            
            # Post-processing to remove echoing of the prompt or standard prefixes
            prefixes_to_strip = ["Response:", "Conclusion:", "Summary:", "Instruction:", "Output:"]
            for prefix in prefixes_to_strip:
                if summary.lower().startswith(prefix.lower()):
                    summary = summary[len(prefix):].strip()
            
            # Fallback if the model still echoes suspiciously long parts of the prompt
            if len(summary) < 5 or "Analysis Data:" in summary:
                return f"The analysis reveals a {ai_text} and identifies the work as {medium_text}. {metadata_text} and {fractal_text} suggest no immediate reasons for concern regarding authenticity."

            return summary

        return "Analysis completed successfully. The image data is consistent with the characteristics of the detected medium."
        
    except Exception as e:
        print(f"Summarization error: {e}")
        return "Analysis completed, but summary generation failed."
