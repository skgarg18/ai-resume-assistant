from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)

RECRUITER_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a helpful AI assistant.

Answer the user's questions using the provided context and the conversation history.

Guidelines:
1. Use the supplied context whenever it is relevant.
2. If the answer is present in the context, answer accurately and concisely.
3. If the answer is not present in the context, clearly state that the information is not available in the provided context.
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