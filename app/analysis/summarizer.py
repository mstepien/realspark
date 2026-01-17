from transformers import pipeline
from threading import Lock
import json

SUMMARIZER_TEMPERATURE = 0.85

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

        # Formatting values for the prompt
        ai_text = f"{ai_prob*100:.1f}% AI probability" if ai_prob is not None else "Unknown AI detection"
        medium_text = f"{medium_info.get('medium', 'Unknown medium')} ({medium_info.get('confidence', 0)*100:.0f}% confidence)"
        metadata_text = "Suspicious metadata findings" if metadata.get('is_suspicious') else "Clean metadata"
        fractal_text = f"Fractal dimension {fractal:.4f}" if fractal else "Standard complexity"

        # Refined prompt with Few-Shot examples
        prompt = (
            f"Instruction: Act as an art appraiser. Write a 3-sentence summary based on the analysis.\n"
            f"Example 1 (Authentic):\n"
            f"AI: 5.2% AI probability, Medium: Oil (95% confidence), Metadata: Clean metadata, Fractal: Fractal dimension 1.8500\n"
            f"Summary: The analysis indicates a very low 5.2% probability of AI generation. The work is identified as an oil painting with standard metadata and expected structural complexity. These factors suggest the piece is likely an authentic human-made work.\n"
            f"Example 2 (AI Generated):\n"
            f"AI: 92.8% AI probability, Medium: Digital (80% confidence), Metadata: Suspicious metadata findings, Fractal: Fractal dimension 1.1000\n"
            f"Summary: The system detected a high 94.8% probability of AI generation. The analysis identified digital characteristics and found suspicious metadata signatures often associated with synthetic media. Given these findings, the work is highly likely AI-generated.\n"
            f"Current Analysis:\n"
            f"AI: {ai_text}, Medium: {medium_text}, Metadata: {metadata_text}, Fractal: {fractal_text}\n"
            f"Current Summary:"
        )

        model = get_summarizer()
        # increased max_length and added cleaning params
        results = model(prompt, max_length=350, do_sample=True, temperature=SUMMARIZER_TEMPERATURE, top_p=0.9)
        
        # Logging raw performance to a specific file
        with open("/app/debug_summarizer.log", "a") as f:
            f.write(f"\n!!!! DEBUG SUMMARIZER START !!!!\n{results}\n!!!! DEBUG SUMMARIZER END !!!!\n")
            f.flush()

        if results and 'generated_text' in results[0]:
            summary = results[0]['generated_text'].strip()
            
            # Post-processing to remove echoing of the prompt or standard prefixes
            prefixes_to_strip = ["Response:", "Conclusion:", "Summary:", "Instruction:"]
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
