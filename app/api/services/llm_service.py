import os
import openai
from typing import Optional, Dict, Any, List
from loguru import logger
from app.core.config import settings

class LLMService:
    """
    Service for interacting with OpenAI's GPT-4 model.
    """
    
    def __init__(self):
        """
        Initialize the LLM service with API key from environment variables.
        """
        self.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-4"
        
        # Check if API key is set
        if not self.api_key:
            logger.warning("OpenAI API key not set. LLM functionality will be limited.")
    
    async def generate_response(self, 
                              prompt: str, 
                              user_message: str, 
                              max_tokens: int = 500, 
                              temperature: float = 0.7) -> Optional[str]:
        """
        Generate a response using GPT-4 based on the provided prompt and user message.
        
        Args:
            prompt: The system prompt that guides the model's behavior
            user_message: The user's message/question
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0-1)
            
        Returns:
            Generated response text or None if there was an error
        """
        try:
            if not self.api_key:
                logger.error("Cannot generate response: OpenAI API key not set")
                return None
                
            # Create the messages for the chat completion
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            # Extract and return the generated text
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                logger.warning("OpenAI API returned empty response")
                return None
                
        except Exception as e:
            logger.error(f"Error generating response from OpenAI API: {str(e)}")
            return None

# Create a singleton instance
llm_service = LLMService()