#summarize using gemini

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Dictionary of summary prompts by type
SUMMARY_PROMPTS = {
    "basic": "Summarize the following text in a concise manner",
    "short": "Summarize the following text in 2-3 sentences",
    "detailed": "Provide a detailed summary of the following text, including key points",
    "bullet_points": "Summarize the following text into bullet points",
    "key_insights": "Extract the key insights from the following text",
    "executive": "Write an executive summary for the following text, focusing on core information",
    "chunked": "Summarize this section of the text clearly and concisely",
    "legal": "Summarize this legal text and highlight any important or unusual clauses",
    "scientific": "Summarize this research paper and highlight its main findings",
    "business": "Summarize this business report, highlighting key financial insights",
    "multi_language": "Summarize the following text (in multiple languages if needed)",
    # Add more ia needed
}

def summarize_text(text: str, summary_type: str = "basic", summary_language: str = "English") -> str:
    """
    Summarizes the given text using Google Gemini 1.5 Pro.
    :param text: The text to be summarized
    :param summary_type: One of the keys in SUMMARY_PROMPTS or defaults to "basic"
    :param summary_language: The desired language of the summary (e.g., "English", "Spanish", etc.)
    :return: The summary text or an error message
    """
    try:
        # Retrieve the prompt template based on summary_type, fallback to "basic"
        prompt_template = SUMMARY_PROMPTS.get(summary_type.lower(), SUMMARY_PROMPTS["basic"])
        
        # Construct final prompt
        # We specify the summary language in the instructions to the model
        final_prompt = (
            f"{prompt_template} in {summary_language}:\n\n"
            f"{text}"
        )

        # Create the Gemini 1.5 Pro model
        model = genai.GenerativeModel("gemini-1.5-pro")

        # Generate the content
        response = model.generate_content(final_prompt)

        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"
