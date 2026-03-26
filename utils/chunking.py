from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunking(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size = )
    text = text.replace("\u200b","")
    content_chunks = []
    paragraphs = splitter.split_text(text)
    for i in range(len(paragraphs)):
        content_chunks.append(f"Paragraph {i+1}: {paragraphs[i]}")
    return content_chunks

