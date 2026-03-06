from google import genai
from dotenv import load_dotenv
import logging
import os

logger = logging.getLogger(__name__)


load_dotenv()

GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

if not GOOGLE_AI_API_KEY:
    logger.debug("GOOGLE_AI_API_KEY is not set in the environment variables.")
else:
    client = genai.Client(api_key=GOOGLE_AI_API_KEY)


    prompt = "Explain the concept of Occam's Razor and provide a simple, everyday example."

    def _call_llm(system_prompt: str, user_payload: str, model: str = "gemini-2.5-pro") -> str:
        """Single point of contact with Google AI; easy to stub in tests."""
        
        logger.info("LLM request: %s tokens", len(user_payload) // 4)
        response = client.models.generate_content(
            model=model,
            contents=[
                system_prompt.strip(),
                user_payload,
            ],
        )
        return response.text
    """ 
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt
    )

    print(response.text)
    """
    ##### WORKING ######

    #print(_call_llm("You are a helpful assistant.", "What is the capital of France?"))  # Example usage