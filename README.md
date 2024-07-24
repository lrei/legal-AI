
# Work-progress
## Data preparation
### Splitting docs
We have written a webscraper using [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/) from bs4that retrieves relevant articles from the [EU AI Act explorer](https://artificialintelligenceact.eu/ai-act-explorer/). For each article we extract its chapter, the date it will become relevant and the summary of the article. We then split each article further into paragraphs, retaining the data extracted above. 

### Converting into json
The format is:
```json
{
    "Chapter": "Chapter III:\nHigh-Risk AI System",
    "Article": "Article 1: Subject Matter",
    "Expected date": "July 2026",
    "Summary": "The EU AI Act requires a risk management system for high-risk AI systems. This system should be a continuous process throughout the AI's lifecycle, regularly reviewed and updated. ....",
    "Paragraph": "2",
    "Text": "The risk management system shall be understood as a continuous iterative process planned and run throughout the entire lifecycle of a high-risk AI system, requiring regular systematic review and updating. It shall comprise the following steps:"
}
```
If we add another "source" document, we should also include the document title.

### Creating a database
We use SQLite database, where properties are named similarly to the json properties. Additionaly, we enumerate the entries. 

### Encoding and storing into vector database
We used model [Legal-BERT](https://huggingface.co/nlpaueb/legal-bert-base-uncased) sentence transformer. 
We stored the vector data into a faiss database [vector_index.faiss](https://github.com/makov3c/ijs/blob/main/data/vector_index.faiss). 

### Retrieval demo
In [retrieval.py](https://github.com/makov3c/ijs/blob/main/retrieval.py) user modifies the `query` variable, to get the desired blocks (Articles). Here we first assign the correct ids for the articles, and then retrieve those from the [blocks.db](https://github.com/makov3c/ijs/blob/main/data/blocks.db) database.
If an error occurs while retrieving (so that the id is not found), we return the error. 

### Test