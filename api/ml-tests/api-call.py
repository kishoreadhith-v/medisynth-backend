import requests
import json

url = "https://api.awanllm.com/v1/chat/completions"

AWANLLM_API_KEY = '9dc8970a-f188-4e2f-b641-deb8178e7d7c	'
MODEL_NAME = 'Awanllm-Llama-3-8B-Dolfin'

payload = json.dumps({
  "model": f"{MODEL_NAME}",
  "messages": [
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': f"Bearer {AWANLLM_API_KEY}"
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)