import requests

api_url = 'http://127.0.0.1:8001/query'

data = {
    'query': '',  # Provide details about your legal matter involving artificial intelligence

    # Set parameters
    'max_articles': 10,  # Maximum number of legal articles you would like to retrieve from European regulations.
    'threshold': 0.5,    # Input a number between 0 and 1 to set the minimum threshold for a legal article to be retrieved. Higher number means stricter article search which is based on cosine similarity.
    'num_responses': 1,  # The number of response variations the LLM model should generate for your input query.
    'sentence_transformer_model': 'BAAI/bge-small-en-v1.5',  # The embedding model used to convert text into numerical vectors for semantic similarity calculations.
    'reranker_model': 'sentence-transformers/all-MiniLM-L6-v2',  # The reranking model that re-evaluates and ranks the retrieved legal articles based on their relevance to your query.
    'openai_model': 'gpt-3.5-turbo',  # The Large Language Model which receives the retrieved articles and generates the prompt, e.g.: "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"...
    'max_tokens': 3000,  # Sets the upper limit on the length of the generated response, measured in tokens.
    'temperature': 0.5,  # Number between 0 and 1 that controls the randomness of the model's responses.
    # Lower values produce more focused and deterministic answers, while higher values result in more creative and varied outputs.
    'prompt_template': '''
    Consider the following articles of legislation, provided between triple backticks, and nothing else:
    ```{context}```

    Under these articles and only these articles, and ignoring those that are not applicable, as a legal compliance expert, answer: what are the implications of the provided articles to the following legal matter, in triple backticks:
    ```{user_query}```

    Answer article by article and don't provide any additional introduction or conclusions.
    Let's think step by step.
    '''
    # A custom prompt template that structures the input for the language model to generate responses.
    # In the prompt you can position the retrieved articles with {context} and your query with {user_query} if needed.
}
# Switching the embedding, reranker or LLM model might require some tweaking of the code in app.py in order to work properly. 
# Embedding models: https://huggingface.co/models?other=embeddings.
# Reranker models: https://huggingface.co/models?other=reranker.
# LLM models: https://llm.datasette.io/en/stable/openai-models.html, https://llm.datasette.io/en/stable/other-models.html.
# For Ollama: https://github.com/taketwo/llm-ollama

headers = {
    'Accept': 'application/json'
}

response = requests.post(api_url, data=data, headers=headers)
if response.status_code == 200:
    json_response = response.json()
    responses = json_response.get('responses', [])
    for idx, res in enumerate(responses, 1):
        print(f"Response {idx}:\n{res}\n")
else:
    print(f"Request failed with status code {response.status_code}")
    print(f"Error message: {response.text}")
