import logging
from config import OPEN_API_KEY
from openai import AsyncOpenAI, OpenAIError, APIConnectionError, RateLimitError
import asyncio

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        if not OPEN_API_KEY:
            raise ValueError("OPEN_API_KEY не встановлено. Неможливо ініціалізувати OpenAIClient.")
        self.client = AsyncOpenAI(api_key=OPEN_API_KEY)
        logger.info("OpenAIClient ініціалізовано.")

    async def ask(self, user_message: str, system_prompt: str = 'You are a helpful assistant') -> str:
        try:
            ukrainian_instruction = "Відповідай виключно українською мовою."
            if system_prompt and system_prompt != 'You are a helpful assistant':
                final_system_prompt = f"{system_prompt} {ukrainian_instruction}"
            else:
                final_system_prompt = f"You are a helpful assistant. {ukrainian_instruction}"

            logger.info(f"Відправлення запиту в OpenAI (текст). Повідомлення: '{user_message[:50]}...'")
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages =[
                    {"role": "system", "content": final_system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            response_content = response.choices[0].message.content
            logger.info(f"Отримано відповідь від OpenAI (текст): '{response_content[:50]}...'")
            return response_content
        except (OpenAIError, APIConnectionError, RateLimitError) as e:
            logger.error(f"Помилка API OpenAI при запиті тексту: {e}")
            raise
        except Exception as e:
            logger.error(f"Непередбачена помилка в OpenAIClient.ask: {e}")
            raise
