import llm_apis.openai_api as openai
import llm_apis.anthropic_api as anthropic
import llm_apis.google_api as google
import logging
from enum import Enum
logger = logging.getLogger(__name__)

class AI_API(Enum):
    
    OPENAI_5 = "gpt-5-2025-08-07"
    
    OPENAI_5_mini = "gpt-5-mini-2025-08-07"

    OPENAI_4o = "gpt-4o"
    
    OPENAI_o4_mini = "o4_mini"

    ANTHROPIC = "claude-opus-4-20250514"

    GOOGLE = "gemini-2.5-pro"

#def make_llm_request(system_prompt, wrapped, llm_model):
#    print(f"Dummy llm request to {llm_model.value} with {len(wrapped) // 4} tokens")
#    return "Dummy response from LLM"

def make_llm_request(system_prompt, wrapped, llm_model, response_format:str = "text"):
    """Make a generic LLM request."""
    try:
        if llm_model == AI_API.OPENAI_o4_mini:
            response = openai.reason(system_prompt, wrapped, response_format=response_format)
        elif llm_model == AI_API.OPENAI_4o:
            response = openai._call_llm(system_prompt, wrapped)
        elif llm_model == AI_API.ANTHROPIC:
            response = anthropic._call_llm(system_prompt, wrapped)
        elif llm_model == AI_API.GOOGLE:
            response = google._call_llm(system_prompt, wrapped)
        return response
    except Exception as e:
        logger.error(f"LLM request failed: {e}")
        return str(e
                   )
        
