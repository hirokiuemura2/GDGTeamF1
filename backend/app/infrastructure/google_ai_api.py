from typing import final
from google import genai
from google.genai import types


@final
class GoogleAIAPIClient:
    def __init__(self, client: genai.Client):
        self.client = client
    
    async def getAdvice(self, message: str):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction = "You are an assistant."),
            contents = message
        )
        return response.text