from groq import Groq
import os
from dotenv import load_dotenv

# Set your Groq API Key here or in your environment variables
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

#------------------------------------------------------------------------------------
#  Groq Client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))