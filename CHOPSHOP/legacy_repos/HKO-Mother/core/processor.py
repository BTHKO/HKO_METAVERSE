import os
import yaml
import requests
from dotenv import load_dotenv

load_dotenv()

class DocumentProcessor:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = self.config.get('processor_model')
        self.offline = self.config.get('offline_mode', False)

    def process(self, text, prompt):
        print(f"--- Processing document with model: {self.model} ---")
        if self.offline:
            print("... OFFLINE MODE: Skipping AI processing.")
            return f"[OFFLINE_PROCESSED]\n\n{text}"

        if not self.api_key:
            print("... ERROR: OPENROUTER_API_KEY not found.")
            return f"[ERROR: API KEY NOT SET]\n\n{text}"

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text}
                    ]
                }
            )
            response.raise_for_status() 
            content = response.json()['choices'][0]['message']['content']
            print("--- AI processing complete. ---")
            return content
        except Exception as e:
            print(f"... ERROR: AI processing failed: {e}")
            return f"[ERROR: API CALL FAILED]\n\n{text}"