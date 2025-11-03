"""
AI-powered description generation service using Ollama
"""
import os
import requests
import json


class AIDescriptionService:
    """Service for generating item names and descriptions from raw user input"""

    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.model = 'phi3'

    def generate_item_details(self, raw_input: str) -> dict:
        """
        Generate structured item details from raw user input

        Args:
            raw_input: User's freeform description of the item

        Returns:
            dict with keys: 'name', 'description'
                - name: Concise label for display/labels (e.g., "10kΩ resistor 1/4W")
                - description: Detailed technical description
        """
        prompt = f"""You are an inventory management assistant. A user described an item, and you need to generate:
1. A concise NAME (suitable for labels/displays, max 50 chars)
2. A detailed DESCRIPTION (technical specs, use case, characteristics)

User's description: "{raw_input}"

Respond ONLY with valid JSON in this exact format:
{{
  "name": "concise name here",
  "description": "detailed technical description here"
}}

Examples:
User: "10k ohm resistor quarter watt"
{{
  "name": "10kΩ resistor 1/4W",
  "description": "Quarter-watt 10 kilohm carbon film through-hole resistor, tolerance ±5%, commonly used for current limiting and voltage division in electronic circuits"
}}

User: "small phillips screwdriver"
{{
  "name": "Phillips screwdriver #1",
  "description": "Small precision Phillips head screwdriver with magnetic tip, size #1, suitable for electronics repair and small appliance assembly"
}}

Now generate for the user's input above. JSON only:"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,  # Lower temperature for more consistent output
                    "options": {
                        "num_predict": 200  # Limit response length
                    }
                },
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # Extract the generated text
            generated_text = result.get('response', '').strip()

            # Try to parse as JSON
            try:
                # Find JSON object in response (in case model added extra text)
                json_start = generated_text.find('{')
                json_end = generated_text.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = generated_text[json_start:json_end]
                    parsed = json.loads(json_str)

                    return {
                        'name': parsed.get('name', raw_input)[:200],  # Limit to DB field size
                        'description': parsed.get('description', raw_input)
                    }
                else:
                    raise ValueError("No JSON object found in response")

            except (json.JSONDecodeError, ValueError) as e:
                print(f"Failed to parse AI response as JSON: {e}")
                print(f"Raw response: {generated_text}")
                # Fallback: use raw input
                return self._fallback_generation(raw_input)

        except requests.exceptions.RequestException as e:
            print(f"Ollama API error: {e}")
            return self._fallback_generation(raw_input)
        except Exception as e:
            print(f"Unexpected error in AI description generation: {e}")
            return self._fallback_generation(raw_input)

    def _fallback_generation(self, raw_input: str) -> dict:
        """Simple fallback when AI is unavailable"""
        # Basic cleanup and capitalization
        cleaned = raw_input.strip()
        name = cleaned[:200] if len(cleaned) <= 200 else cleaned[:197] + '...'

        return {
            'name': name,
            'description': cleaned
        }


# Singleton instance
ai_description_service = AIDescriptionService()
