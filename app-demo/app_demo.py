from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
import yaml
import uvicorn
import llm

# Load configuration from the config file
with open('app-demo/config_demo.yaml', 'r') as f:
    config = yaml.safe_load(f)

app = FastAPI(
    title="AI Legal Assistant API",
    description="An API to retrieve legal articles and generate responses using LLMs.",
    version="1.0.0"
)

# Add SessionMiddleware for session management
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))

templates = Jinja2Templates(directory="app-demo")

def get_chatgpt_response(prompt, max_tokens, model_name, num_responses, temperature, api_key):
    # Set the OpenAI API key for llm
    llm.api_key = api_key

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
    return templates.TemplateResponse('ui_demo.html', {
        'request': request,
        'config': config,
        'session': request.session
    })

@app.post("/query")
def query(
    request: Request,
    query: str = Form(..., description="Describe your legal matter."),
    max_tokens: int = Form(..., description="Maximum tokens for the LLM response."),
    openai_model: str = Form(..., description="OpenAI model to use."),
    max_articles: int = Form(..., description="Maximum number of articles to retrieve."),
    threshold: float = Form(..., description="Cosine similarity threshold."),
    num_responses: int = Form(..., description="Number of responses to generate."),
    temperature: float = Form(..., description="Temperature for the LLM."),
    sentence_transformer_model: str = Form(..., description="Sentence Transformer model to use."),
    reranker_model: str = Form(..., description="Reranker model to use."),
    prompt_template: str = Form(..., description="Prompt template to use."),
    api_key: str = Form(None, description="OpenAI API Key."),
    store_api_key: str = Form(None, description="Store API Key for the session."),
    param_choice: str = Form('custom', description="Parameter choice: default or custom.")
):
    session = request.session
    user_query = query
    error_message = ''

    # Handle API Key
    if not api_key:
        # Try to get the API key from the session
        api_key = session.get('api_key')

    if not api_key:
        error_message = "Please provide your OpenAI API Key."
        prompt = ''
        responses = []
    else:
        # Store API Key if user chose to store it
        if store_api_key == 'on':
            session['api_key'] = api_key
        else:
            session.pop('api_key', None)  # Remove API key from session if not storing

        # Use default parameters if selected
        if param_choice == 'default':
            max_tokens = config.get('max_tokens', 3000)
            openai_model = config.get('openai_model', 'gpt-3.5-turbo')
            max_articles = config.get('max_articles', 8)
            threshold = config.get('threshold', 0.5)
            num_responses = config.get('num_responses', 1)
            temperature = config.get('temperature', 0.5)
            sentence_transformer_model = config.get('sentence_transformer_model', 'BAAI/bge-small-en-v1.5')
            reranker_model = config.get('reranker_model', 'sentence-transformers/all-MiniLM-L6-v2')
            prompt_template = config.get('prompt_template', '')
        # Else, use the parameters provided by the user

        # Proceed with generating the response
        try:
            relevant_chunks = retrieve_chunks(
                user_query,
                max_articles=int(max_articles),
                threshold=float(threshold),
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
                num_responses=int(num_responses),
                temperature=float(temperature),
                api_key=api_key  # Pass the API key
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
            'ui_demo.html',
            {
                'request': request,
                'user_query': user_query,
                'prompt': prompt,
                'responses': responses,
                'config': config,
                'error_message': error_message,
                'session': session  # Pass the session to the template
            }
        )

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8001)
