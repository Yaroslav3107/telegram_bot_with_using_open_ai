from config import OPEN_API_KEY
from openai import AsyncOpenAI, OpenAIError
import asyncio

class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPEN_API_KEY)

    async def ask(self, user_message, system_prompt: str = 'You are helpful assistance') -> str:
        try:
            response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages =[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            raise


async def main():
    client = OpenAIClient()
    reply = await client.ask("Hi, whats up?")
    print(reply)

if __name__ == "__main__":
    asyncio.run(main())