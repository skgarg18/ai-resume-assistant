from groq import Groq
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Set your Groq API Key here or in your environment variables
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

#------------------------------------------------------------------------------------
#  Groq Client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

#-----------------------------------------------------------------------------------------
#  LLM Model

llm_model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)