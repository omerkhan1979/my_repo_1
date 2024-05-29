import google.generativeai as genai

genai.configure(api_key="GOOGLE_API_KEY")
GOOGLE_API_KEY = "AIzaSyDYTXLDIyDO0SQZ_YpXr3Spw7nOY2z9qgQ"  # Replace with your actual API key
print(GOOGLE_API_KEY)

import google.generativeai as genai

# (Optional) List available models
models = [m for m in genai.list_models() if "chat-bison" in m.model_name]
print(models)

# Instantiate a model
model = genai.GenerativeModel(model=models[0].model_name)  # or specify model directly
model.temperature = 0.7
model.top_p = 0.95
model.top_k = 40

# Generate text
prompt = "What is the capital of France?"
response = model.generate_text(
    prompt=prompt
)

print(f"Prompt: {prompt}")
print(f"Response: {response.result}")
