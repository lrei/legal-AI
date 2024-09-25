from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

def retrieve_chunks(query_text):
    result = subprocess.run(
        ['python', 'retrieving_articles.py', query_text],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('-----\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_query = request.form['query']
    relevant_chunks = retrieve_chunks(user_query)
    context = "\n".join(relevant_chunks)

    # Pre-defined prompt template
    prompt = (
        f"Consider the following articles of legislation, provided between triple backticks, "
        f"and nothing else:\n```\n{context}\n```\n\n"
        f"Under these articles and only these articles, and ignoring those that are not "
        f"applicable, as a legal compliance expert, answer: what are the implications of the "
        f"provided articles to the following legal matter, in triple backticks:\n"
        f"```\n{user_query}\n```\n"
        f"Answer article by article and don't provide any additional introduction or "
        f"conclusions.\nLet's think step by step."
    )
    return render_template(
        'index.html',
        user_query=user_query,
        prompt=prompt,
        relevant_chunks=relevant_chunks
    )

if __name__ == '__main__':
    app.run(debug=True)
