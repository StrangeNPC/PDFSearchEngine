
# PDF Search Engine


The PDF Search Engine is a python application that is mean't for directories with large amounts of PDF documents that are too numerous to perfrom manual search.

It is mean't to be an answer to semantic-search AI question answering systems that hallucinate or become ineffective as scale of documents increases.


![download page](https://github.com/StrangeNPC/PDFSearchEngine/assets/95240891/ff4b8f57-3824-4ac2-8121-6f6111a1e2d6)



## Prerequisites

1. Clone the repository to your local machine.

```bash
git clone https://github.com/StrangeNPC/PDFSearchEngine.git
```

2. Install required packages using the following command.

```bash
pip install -r requirements.txt
```
3. Run Django Server

```bash
streamlit run StreamlitPDF.py

```
## Usage/Examples


1. Build the index:

Click on the "Build Index" button in the sidebar. This will create an index of the PDF files in the "SourceDocuments" directory.


2. Select the documents to search:

Choose the PDF files you want to include in the search by selecting them from the multiselect checkbox in the sidebar. By default, all the documents are selected.


3. Enter a search query:

Type your search query in the input box below the document selection. Press the "Enter" key or click the "Search" button to perform the search.

4. View search results:

The search results will be displayed below the search input box. Each result includes the file name, page number, and the relevant paragraph containing the search query terms.

5. Download search result pages:

Click on the "Download Page <page_number>" button to download the specific page from the search results as a separate PDF file.


## Contributing

Contributions are welcome. Please create an issue or submit a pull request if you want to contribute to this project.



## License

[MIT](https://choosealicense.com/licenses/mit/)

