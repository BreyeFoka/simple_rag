import ollama
from data_loader import load_cat_facts
from vector_db import add_chunk_to_db, get_all_chunks_and_embeddings, clear_db

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

dataset = []

def cosine_similarity(a, b):
    dot_product = sum([x * y for x, y in zip(a, b)])
    norm_a = sum([x ** 2 for x in a]) ** 0.5
    norm_b = sum([x ** 2 for x in b]) ** 0.5
    return dot_product / (norm_a * norm_b)

def retrieve(query, top_n=3):
    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
    similarities = []
    for chunk, embedding in get_all_chunks_and_embeddings():
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk, similarity))
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

def initialize_db():
    clear_db()
    dataset = load_cat_facts('cat-facts.txt')
    # Log the loading for debug
    # print(f'Loaded {len(dataset)} entries')
    for i, chunk in enumerate(dataset):
        embedding = ollama.embed(model=EMBEDDING_MODEL, input=chunk)['embeddings'][0]
        add_chunk_to_db(chunk, embedding)
        # print the log for debug
        # print(f'Added chunk {i+1}/{len(dataset)} to the database')

def main():
    initialize_db()
    print("Welcome to the Cat Facts Chatbot! Type 'exit' or 'quit' to end the chat.")
    while True:
        input_query = input('Ask me a question: ')
        if input_query.strip().lower() in ['exit', 'quit']:
            print('Goodbye!')
            break
        retrieved_knowledge = retrieve(input_query)
        #no need to log the retrived knowledge
        # print('Retrieved knowledge:')
        # for chunk, similarity in retrieved_knowledge:
        #     print(f' - (similarity: {similarity:.2f}) {chunk}')
        instruction_prompt = f'''You are a helpful chatbot.\nUse only the following pieces of context to answer the question. Don't make up any new information:\n{'\n'.join([f' - {chunk}' for chunk, similarity in retrieved_knowledge])}\n'''
        stream = ollama.chat(
            model=LANGUAGE_MODEL,
            messages=[
                {'role': 'system', 'content': instruction_prompt},
                {'role': 'user', 'content': input_query},
            ],
            stream=True,
        )
        print('Chatbot response:')
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)
        print()  # for spacing

if __name__ == '__main__':
    main()
  