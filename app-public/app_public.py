### App version accessible to a public user - default parameters used.
### Start the app by running this Python file or via cmd.

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import yaml
import uvicorn
import llm
from examples import examples  # Import the updated examples

# Load configuration from the config file
with open('app-public/config_public.yaml', 'r') as f:
    config = yaml.safe_load(f)

app = FastAPI(
    title="AI Legal Assistant API",
    description="An API to retrieve legal articles and generate responses using LLMs.",
    version="1.0.0"
)

templates = Jinja2Templates(directory="app-public")

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

            cleaned_text = response.text().strip().replace('```', '')
            responses.append(cleaned_text)
        except Exception as e:
            print(f"An error occurred during model prompting: {e}")
            responses.append("")
    return responses

def format_article_title(articles):
    formatted_articles = []
    for article in articles:
        lines = article.split('\n')
        if len(lines) >= 3:
            # Make the third line (article title) bold
            lines[2] = f"<strong>{lines[2]}</strong>"
        formatted_articles.append('\n'.join(lines))
    return formatted_articles

def retrieve_chunks(query_text, max_articles, threshold, sentence_transformer_model, reranker_model):
    from retrieving_articles import retrieve_articles
    articles = retrieve_articles(
        query_text,
        k=max_articles,
        threshold=threshold,
        sentence_transformer_model=sentence_transformer_model,
        reranker_model=reranker_model
    )
    
    # Format article titles (make third line bold)
    formatted_articles = format_article_title(articles)
    
    return formatted_articles

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('ui_public.html', {'request': request, 'config': config, 'examples': examples})

@app.post("/query")
def query(
    request: Request,
    query: str = Form(..., description="Describe your legal matter."),
    api_key: str = Form(..., description="OpenAI API Key.")
):
    user_query = query
    error_message = ''

    if not api_key:
        error_message = "Please provide your OpenAI API Key."
        prompt = ''
        responses = []
    else:
        # Use parameters from config
        max_tokens = config.get('max_tokens', 3000)
        openai_model = config.get('openai_model', 'gpt-3.5-turbo')
        max_articles = config.get('max_articles', 8)
        threshold = config.get('threshold', 0.5)
        num_responses = config.get('num_responses', 1)
        temperature = config.get('temperature', 0.5)
        sentence_transformer_model = config.get('sentence_transformer_model', 'BAAI/bge-small-en')
        reranker_model = config.get('reranker_model', 'sentence-transformers/all-MiniLM-L6-v2')
        prompt_template = config.get('prompt_template', '')

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
                temperature=temperature,
                api_key=api_key
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
        # Pass 'examples' to the template
        return templates.TemplateResponse(
            'ui_public.html',
            {
                'request': request,
                'user_query': user_query,
                'prompt': prompt,
                'responses': responses,
                'config': config,
                'error_message': error_message,
                'examples': examples
            }
        )

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8001)

