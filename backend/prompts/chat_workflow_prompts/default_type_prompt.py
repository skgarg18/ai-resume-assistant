from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)

DEFAULT_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a helpful AI assistant.

Answer the user's questions using the provided context and the conversation history.

Guidelines:
1. Use the supplied context whenever it is relevant.
2. If the answer is present in the context, answer accurately and concisely.
3. If the requested information is not present in the resume, respond naturally by saying that the resume does not mention or contain that information. Avoid phrases like "the provided context does not specify" or "the context is missing."
4. Do not make up facts or hallucinate information.
5. Maintain a natural conversational tone.
6. Consider the chat history when answering follow-up questions.
"""
    ),

    MessagesPlaceholder("chat_history"),

    (
        "human",
        """
Context:
{context}

Question:
{question}
"""
    )
])