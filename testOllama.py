import requests
import json
import weaviate
o = weaviate.WeaviateAsyncClient()
o.collections.get("Pwc_global_db").generate.hybrid()

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

# Define request payload
payload = {
    "model": "bge-large", 
    "prompt": "Can you write an essay on India under 100 words"
}

# Send request
# response = requests.post(OLLAMA_URL, json=payload)

# Parse response
# if response.status_code == 200:
#     result = response.json()
#     print("Response:", result["response"])
# else:
#     print("Error:", response.text)

with requests.post(OLLAMA_URL, json=payload, stream=True) as response:
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            print(data.get("response", ""), end="", flush=True)
