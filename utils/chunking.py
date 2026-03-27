from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunking(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
    text = text.replace("\u200b","")
    content_chunks = []
    paragraphs = splitter.split_text(text)
    for i in range(len(paragraphs)):
            content_chunks.append(paragraphs[i])
            
    return content_chunks

