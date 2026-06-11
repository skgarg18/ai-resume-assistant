import chromadb

#---------------------------------------------------------------------------------
# Vector DB (ChromaDB runs locally in memory for this MVP)
chroma_client = chromadb.Client()
# Creating collection to store embeddings of all resumes
collection = chroma_client.get_or_create_collection(name="resumes")
# Creating collection to chunks of top resumes
chat_collection = chroma_client.get_or_create_collection(
    name="chat_chunks"
)