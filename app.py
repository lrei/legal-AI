from flask import Flask, request, jsonify, render_template
import subprocess

app = Flask(__name__)

def retrieve_chunks(query_text):
    result = subprocess.run(['python', 'vec-encoding.py', query_text], capture_output=True, text=True)
    return result.stdout.strip().split('\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_query = request.form['query']
    relevant_chunks = retrieve_chunks(user_query)
    additional_instructions = "Provide a concise and informative response based on the relevant information provided."
    context = "\n".join(relevant_chunks)
    prompt = f"User Query: {user_query}\n\nRelevant Information:\n{context}\n\nInstructions:\n{additional_instructions}"
    return render_template('index.html', user_query=user_query, prompt=prompt, relevant_chunks=relevant_chunks)

if __name__ == '__main__':
    app.run(debug=True)