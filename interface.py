import openai
import subprocess

import os
openai.api_key = os.getenv('OPENAI_API_KEY')


def get_chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        print(f"An error occurred: {e}")
        return None


def retrieve_chunks(query_text):
    result = subprocess.run(['python', 'retrieving_articles.py', query_text], capture_output=True, text=True)
    return result.stdout.strip().split('-----\n')

def main():
    user_query = input("Enter your query: ")
    relevant_chunks = retrieve_chunks(user_query)
    context = "\n".join(relevant_chunks)

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

    print("\nConstructed Prompt:")
    print(prompt)

    response = get_chatgpt_response(prompt)

    print("\nResponse from ChatGPT:")
    print(response)

if __name__ == "__main__":
    main()
