# Le contenu COMPLET et MIS A JOUR du fichier.
# N'incluez que le code final, pas de diffs ou d'explications.
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI
try:
    genai_api_key = os.getenv("GENAI_API_KEY")
    if genai_api_key:
        genai.configure(api_key=genai_api_key)
    else:
        logging.warning("GENAI_API_KEY not found in environment variables. Gemini API calls may fail.")
except Exception as e:
    logging.error(f"Error configuring Google Generative AI: {e}")

# Configure Vertex AI
try:
    # This assumes the environment is authenticated, e.g., via `gcloud auth application-default login`
    # or the GOOGLE_APPLICATION_CREDENTIALS environment variable is set.
    # Project and location details are taken from the project context.
    PROJECT_ID = "healthy-fuze-437202-j9"
    LOCATION = "us-central1"  # A common default, can be parameterized if needed
    vertexai.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    logging.warning(f"Vertex AI initialization failed: {e}. Vertex AI calls may fail.")


# --- Helper Functions ---

def load_prompt_template(template_path: str) -> str:
    """Loads a prompt template from the given file path."""
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Prompt template file not found at: {template_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading prompt template {template_path}: {e}")
        raise


def summarise_with_gemini_api(prompt: str) -> str:
    """Summarises content using the Google Gemini Pro API via google-generativeai."""
    logging.info("Summarizing with Gemini API...")
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text


def summarise_with_vertex_ai(prompt: str) -> str:
    """Summarises content using a Gemini model on Vertex AI."""
    logging.info("Summarizing with Vertex AI...")
    model = GenerativeModel("gemini-1.0-pro")
    response = model.generate_content(prompt)
    return response.text


def get_summary(item: dict, prompt_template_path: str, model_function) -> str:
    """
    Generates a summary for a given item using a specified model function and prompt template.
    """
    prompt_template = load_prompt_template(prompt_template_path)
    # The item dictionary keys must match the placeholders in the prompt template
    prompt = prompt_template.format(**item)
    summary = model_function(prompt)
    return summary


# --- Core Logic ---

def process_list_of_items(items: list, prompt_template_path: str, primary_model_name: str = 'gemini', secondary_model_name: str = 'vertexai') -> list:
    """
    Processes a list of content items, summarizing each one.

    It attempts to use a primary model for summarization. If that fails, it
    falls back to a secondary model. If both models fail, the item is still
    included in the final list, but its 'summary' field contains an error
    message indicating the failure.

    Args:
        items: A list of dictionaries, where each dictionary represents a
               content item (e.g., video, article).
        prompt_template_path: The file path to the prompt template to use for summarization.
        primary_model_name: The name of the primary model to use ('gemini' or 'vertexai').
        secondary_model_name: The name of the fallback model to use ('gemini' or 'vertexai').

    Returns:
        A list of processed items, with a 'summary' key added to each item.
    """
    processed_items = []

    model_map = {
        'gemini': summarise_with_gemini_api,
        'vertexai': summarise_with_vertex_ai
    }

    primary_model_func = model_map.get(primary_model_name)
    secondary_model_func = model_map.get(secondary_model_name)

    if not primary_model_func:
        raise ValueError(f"Primary model '{primary_model_name}' is not valid. Choose from {list(model_map.keys())}.")
    if not secondary_model_func:
        raise ValueError(f"Secondary model '{secondary_model_name}' is not valid. Choose from {list(model_map.keys())}.")

    for item in items:
        summary = None
        item_title = item.get('title', 'Unknown Item')
        
        try:
            logging.info(f"Attempting to summarize '{item_title}' with primary model ({primary_model_name})...")
            summary = get_summary(item, prompt_template_path, primary_model_func)
            logging.info(f"Successfully summarized '{item_title}' with primary model.")
        except Exception as e:
            logging.warning(f"Primary model ({primary_model_name}) failed for item '{item_title}': {e}")
            try:
                logging.info(f"Attempting to summarize '{item_title}' with secondary model ({secondary_model_name})...")
                summary = get_summary(item, prompt_template_path, secondary_model_func)
                logging.info(f"Successfully summarized '{item_title}' with secondary model.")
            except Exception as e2:
                logging.error(f"Secondary model ({secondary_model_name}) also failed for item '{item_title}': {e2}")
                summary = "Error: Summarization failed for this item with all available models."

        # Create a copy to avoid modifying the original list of dictionaries in place
        item_copy = item.copy()
        item_copy['summary'] = summary
        processed_items.append(item_copy)

    return processed_items