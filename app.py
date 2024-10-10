from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import yaml
import uvicorn
import llm

# Load configuration from config.yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

app = FastAPI(
    title="AI Legal Assistant API",
    description="An API to retrieve legal articles and generate responses using LLMs.",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

def get_chatgpt_response(prompt, max_tokens, model_name, num_responses, temperature):
    # Set the OpenAI API key for llm
    llm.api_key = os.getenv('OPENAI_API_KEY')

    try:
        model = llm.get_model(model_name)
    except llm.UnknownModelError:
        print(f"Model '{model_name}' is not recognized by the llm library.")
        return []

    responses = []

    for _ in range(num_responses):
        try:
            # Generate the response
            response = model.prompt(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            # Clean the response by removing triple backticks
            cleaned_text = response.text().strip().replace('```', '')
            responses.append(cleaned_text)
        except Exception as e:
            print(f"An error occurred during model prompting: {e}")
            responses.append("")
    return responses


def retrieve_chunks(query_text, max_articles, threshold, sentence_transformer_model, reranker_model):
    from retrieving_articles import retrieve_articles
    articles = retrieve_articles(
        query_text,
        k=max_articles,
        threshold=threshold,
        sentence_transformer_model=sentence_transformer_model,
        reranker_model=reranker_model
    )
    return articles

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('ui.html', {'request': request, 'config': config})

@app.post("/query")
def query(
    request: Request,
    query: str = Form(..., description="Describe your legal matter."),
    max_tokens: int = Form(default=config.get('max_tokens', 3000), description="Maximum tokens for the LLM response."),
    openai_model: str = Form(default=config.get('openai_model', 'gpt-3.5-turbo'), description="OpenAI model to use."),
    max_articles: int = Form(default=config.get('max_articles', 8), description="Maximum number of articles to retrieve."),
    threshold: float = Form(default=config.get('threshold', 0.4), description="Cosine similarity threshold."),
    num_responses: int = Form(default=config.get('num_responses', 1), description="Number of responses to generate."),
    temperature: float = Form(default=config.get('temperature', 0.5), description="Temperature for the LLM."),
    sentence_transformer_model: str = Form(default=config.get('sentence_transformer_model', 'BAAI/bge-small-en'), description="Sentence Transformer model to use."),
    reranker_model: str = Form(default=config.get('reranker_model', 'sentence-transformers/all-MiniLM-L6-v2'), description="Reranker model to use."),
    prompt_template: str = Form(default=config.get('prompt_template', ''), description="Prompt template to use.")
):
    user_query = query
    error_message = ''

    try:
        relevant_chunks = retrieve_chunks(
            user_query,
            max_articles=max_articles,
            threshold=threshold,
            sentence_transformer_model=sentence_transformer_model,
            reranker_model=reranker_model
        )
        context = "\n".join(relevant_chunks)

        # Check if placeholders are present
        if '{context}' not in prompt_template or '{user_query}' not in prompt_template:
            # Use default prompt
            prompt_template = config.get('prompt_template', '')
            if '{context}' not in prompt_template or '{user_query}' not in prompt_template:
                error_message = "The default prompt template is invalid. Please ensure it contains {context} and {user_query} placeholders."
                raise ValueError(error_message)
            else:
                prompt = prompt_template.format(context=context, user_query=user_query)
        else:
            prompt = prompt_template.format(context=context, user_query=user_query)

        responses = get_chatgpt_response(
            prompt,
            max_tokens=int(max_tokens),
            model_name=openai_model,
            num_responses=num_responses,
            temperature=temperature
        )
    except Exception as e:
        error_message = str(e)
        prompt = ''
        responses = []

    accept_header = request.headers.get('Accept', '')
    if 'application/json' in accept_header:
        return JSONResponse({
            'user_query': user_query,
            'prompt': prompt,
            'responses': responses,
            'error_message': error_message
        })
    else:
        return templates.TemplateResponse(
            'ui.html',
            {
                'request': request,
                'user_query': user_query,
                'prompt': prompt,
                'responses': responses,
                'config': config,
                'error_message': error_message
            }
        )

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8001)
