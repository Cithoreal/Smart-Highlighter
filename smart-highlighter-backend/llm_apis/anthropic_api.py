import anthropic
from dotenv import load_dotenv
import logging
import os

logger = logging.getLogger(__name__)


load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    logger.debug("ANTHROPIC_API_KEY is not set in the environment variables.")
else:
    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=ANTHROPIC_API_KEY,
    )

    def _call_llm(system_prompt: str, user_payload: str, model: str = "claude-opus-4-20250514") -> str:
        """Single point of contact with Anthropic; easy to stub in tests."""
        
        logger.info("LLM request: %s tokens", len(user_payload) // 4)
        response = client.messages.create(
            model=model,
            max_tokens=8000,
            temperature=0.2,
            messages=[
                {"role": "user", "content": system_prompt.strip()},
                {"role": "user", "content": user_payload},
            ],
        )
        return response.content[0].text

    """ message = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Hello, Claude"}
        ]
    )
    print(message.content) """

    ###### WORKING ######

    #print(_call_llm("You are a helpful assistant.", "What is the capital of France?"))  # Example usage