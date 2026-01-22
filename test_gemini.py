from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest")
try:
    response = llm.invoke("Say hello!")
    print("Success:", response.content)
except Exception as e:
    print("Failed:", e)