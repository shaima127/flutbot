from groq import Groq
from app.core.config import config
import json

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)

    async def generate_response(self, prompt: str, context: str = "", model: str = "llama3-8b-8192"):
        system_prompt = f"""
        You are a highly experienced Flutter developer and teacher. 
        Your goal is to teach Flutter in a clear, friendly, and efficient way.
        Always provide code snippets where relevant and explain them.
        Use Arabic if the user asks in Arabic.
        
        Context from Flutter Documentation:
        {context}
        """
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model=model,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content

    async def evaluate_test(self, answers: str):
        prompt = f"Evaluate the following user answers for a Flutter placement test. Based on the accuracy, assign a level: 'beginner', 'intermediate', or 'advanced'. Respond ONLY with the level name.\nAnswers: {answers}"
        return await self.generate_response(prompt)

groq_service = GroqService()
