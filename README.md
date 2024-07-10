
# Work-progress
## Data preparation
### Splitting docs
In [[doc-split.py]] we split the (specific) EU legalisation document into appropriate sections (first by articles, and then the introduction by definitions). We save those sections into [[sections.txt]],  where they are separated by `\n---\n`. 

### Converting into json
The format is:
```json
{
    "text": "(2)\nThis Regulation should be applied in accordance with the values of the Union enshrined \nas in the Charter, facilitating the protection of natural persons, undertakings, \ndemocracy, the rule of law and environmental protection, while boosting innovation and \nemployment and making the Union a leader in the uptake of trustworthy AI.\nEN\nUnited in diversity\nEN\n",
    "position": 2
},
```
If we add another "source" document, we should also include the document title.

### Creating a database
We used SQLite database.

### Encoding and storing into vector database
We used all-MiniLM-L6-v2 sentence transformer. 
We stored the vector data into a faiss database [vector_index.faiss]. 

### Retrieval demo
In [retrieval.py] user modifies the `query` variable, to get the desired blocks (Articles). Here we first assign the correct ids for the articles, and then retrieve those from the [blocks.db] database.
If an error occurs while retrieving (so that the id is not found), we return the error. 