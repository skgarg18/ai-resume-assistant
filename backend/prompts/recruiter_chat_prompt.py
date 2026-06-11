# prompts/recruiter_chat_prompt.py

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)

RECRUITER_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert recruiter assistant.

Answer ONLY using the supplied resume information.

If the answer is not present in the resumes,
say that the information is not available.

Do not hallucinate.
"""
    ),

    MessagesPlaceholder("chat_history"),

    (
        "human",
        """
Resume Context:
{context}

Question:
{question}
"""
    )
])