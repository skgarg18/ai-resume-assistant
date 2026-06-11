from langchain_text_splitters import RecursiveCharacterTextSplitter

#----------------------------------------------------------------------------------------
#  Splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)