import json
import re
import os 

from abc import ABC, abstractmethod
from openai import OpenAI

class BaseOCREngine(ABC):
    @abstractmethod
    def readtext(self, image_url: str) -> dict:
        """
        Perform OCR on the given image and return a list of:
        (bounding_box, text, confidence)
        """
        pass

class ChatGPTEngine(BaseOCREngine):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Vision-capable model

    def readtext(self, image_url: str):
        """
        Sends an image URL plus prompt to the GPT vision model,
        returns parsed JSON or raw string response.
        """
        if "media.rightmove.co.uk" not in image_url:
            raise ValueError(f"Image URL must be from media.rightmove.co.uk domain. Got: {image_url}")
        
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that reads and extracts data from EPC graphs."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this EPC image and return current and potential EPC ratings in JSON. I only need the numeric ratings and please use only current and potential as keys. Sometimes there are two charts, in which case the one to look at is the Energy Efficiency Rating chart."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=300,
        )

        content = response.choices[0].message.content
        print("[DEBUG] API response content:", content)

        # Extract the JSON block between triple backticks
        match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            json_text = match.group(1)
            try:
                data = json.loads(json_text)
                return data
            except json.JSONDecodeError:
                print("Failed to parse JSON block.")
                return json_text
        else:
            print("No JSON block found. Returning raw content.")
            return content