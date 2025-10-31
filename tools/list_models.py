import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("可用模型列表：\n")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)

