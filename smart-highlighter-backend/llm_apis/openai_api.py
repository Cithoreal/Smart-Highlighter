from dotenv import load_dotenv
import openai
import logging
import os

logger = logging.getLogger(__name__)


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#if empty, exit file
if not OPENAI_API_KEY:
    logger.debug("OPENAI_API_KEY is not set in the environment variables.")
else:
    openai.api_key = OPENAI_API_KEY
    client = openai.OpenAI()

    def _call_llm(system_prompt: str, user_payload: str, model: str = "gpt-4o", respond_json:bool = False) -> str:
        """Single point of contact with OpenAI; easy to stub in tests."""
        
        logger.info("LLM request: %s tokens", len(user_payload) // 4)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_payload},
            ],
        )
        return response.choices[0].message.content

    def reason(system_prompt: str, user_prompt: str, model = "o4-mini",  response_format:str = "text") -> str:
        """Call the LLM with a reasoning prompt."""
        response = client.responses.create(
            model = model,
            reasoning = {"effort": "high"},
            text = {
                "format": {
                    "type": response_format
            }},
            input = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        return response.output_text