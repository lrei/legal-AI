import openai
import subprocess

openai.api_key = 'your-openai-api-key'

def get_chatgpt_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def retrieve_chunks(query_text):
    result = subprocess.run(['python', 'vec-encoding.py', query_text], capture_output=True, text=True)
    return result.stdout.strip().split('\n')

def main():
    user_query = input("Enter your query: ")
    
    relevant_chunks = retrieve_chunks(user_query)
    additional_instructions = "Provide a concise and informative response based on the relevant information provided."
    
    context = "\n".join(relevant_chunks)
    
    prompt = f"User Query: {user_query}\n\nRelevant Information:\n{context}\n\nInstructions:\n{additional_instructions}"
    
    print("\nConstructed Prompt:")
    print(prompt)
    
    response = get_chatgpt_response(prompt)
    
    print("\nResponse from ChatGPT:")
    print(response)

if __name__ == "__main__":
    main()
