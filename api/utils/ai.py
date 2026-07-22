import os
import openai
import PyPDF2
import numpy as np

def get_embedding(text, model="text-embedding-ada-002"):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if not openai.api_key:
        return []
    try:
        text = text.replace("\nfrom ..repositories.knowledge_repository import KnowledgeRepository\n\n", " ")
        response = openai.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return []

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if vec1.shape != vec2.shape:
        return 0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def chunk_text(text, max_length=1000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if current_length >= max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def process_pdf_and_store(client, document):
    from api.models import KnowledgeChunk
    text = extract_text_from_pdf(document.file.path)
    if not text:
        return False
        
    chunks = chunk_text(text)
    
    for chunk_text_data in chunks:
        embedding = get_embedding(chunk_text_data)
        if embedding:
            KnowledgeRepository.create_knowledgechunk(
                client=client,
                document=document,
                content=chunk_text_data,
                embedding=embedding
            )
    return True

def retrieve_relevant_chunks(client, query, top_k=3):
    from api.models import KnowledgeChunk
    query_embedding = get_embedding(query)
    if not query_embedding:
        return []
        
    chunks = KnowledgeRepository.filter_chunks(client=client)
    scored_chunks = []
    
    for chunk in chunks:
        if chunk.embedding:
            similarity = cosine_similarity(query_embedding, chunk.embedding)
            scored_chunks.append((similarity, chunk.content))
            
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk[1] for chunk in scored_chunks[:top_k]]

def generate_ai_response(client, query):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if not openai.api_key:
        return "Sorry, AI is currently disabled (API key missing)."
        
    # Get relevant context from Knowledge Base
    relevant_chunks = retrieve_relevant_chunks(client, query)
    context = "\n".join(relevant_chunks)
    
    system_prompt = f"""You are a helpful assistant for a business.
Business Context:
{client.ai_context}

Here is some relevant knowledge from the company's knowledge base:
{context}

Answer the user's query based ONLY on the provided knowledge base and business context.
If you don't know the answer, politely state that you cannot help with that query.
Keep your response concise and conversational (like a WhatsApp message)."""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3,
            max_tokens=250
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "I'm having trouble processing that right now. Please try again later."
