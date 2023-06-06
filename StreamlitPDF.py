import os
import re
import streamlit as st
from PyPDF2 import PdfReader 
from whoosh import fields, index
from whoosh.qparser import QueryParser
from whoosh.index import create_in, open_dir
from whoosh.filedb.filestore import RamStorage

def create_index(directory):
    schema = fields.Schema(file_path=fields.TEXT(stored=True),
                           page_number=fields.NUMERIC(stored=True),
                           content=fields.TEXT(stored=True))
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    ix = create_in(directory, schema)
    writer = ix.writer()
    
    # Index the PDF files
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "rb") as file:
                pdf = PdfReader (file)
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text().replace('\n', ' ')
                    
                    writer.add_document(file_path=file_path,
                                        page_number=page_num + 1,
                                        content=text)
                    st.write("Indexed:", file_path, "Page:", page_num + 1)
    
    writer.commit()
    return ix

def search_index(index_dir, search_query):
    ix = open_dir(index_dir)
    query = QueryParser("content", ix.schema).parse(search_query)
    with ix.searcher() as searcher:
        hits = searcher.search(query)
        results = []
        for hit in hits:
            stored_fields = searcher.stored_fields(hit.docnum)
            file_path = stored_fields["file_path"]
            page_number = stored_fields["page_number"]
            content = stored_fields["content"]
            paragraphs = content.split("\n\n")  # Split content into paragraphs

            # Find the paragraph containing the query terms
            matched_paragraph = None
            for paragraph in paragraphs:
                if search_query.lower() in paragraph.lower():
                    matched_paragraph = paragraph
                    break

            if matched_paragraph:
                result = {
                    "file_path": file_path,
                    "page_number": page_number,
                    "paragraph": matched_paragraph
                }
                results.append(result)
    return results


def highlight_query_terms(paragraph, query):
    highlighted_paragraph = re.sub(
        fr"\b({re.escape(query)})\b",
        r'<mark style="background-color: yellow;">\1</mark>',
        paragraph,
        flags=re.IGNORECASE
    )
    return highlighted_paragraph

# Streamlit app code
def main():
    st.title("PDF Search Engine")
    
    # Get the current directory path and redirect to SourceDocuments folder
    current_dir = os.getcwd()
    index_dir = os.path.join(current_dir, "SourceDocuments")
    
    st.sidebar.subheader("Search Options")
    placeholder = st.sidebar.empty()  # Create an empty placeholder

    if st.sidebar.button("Build Index"):
        create_index(index_dir)
        st.sidebar.write("Index created successfully.")
    
    search_query = placeholder.text_input("Enter search query", key="search_input")
    
    if st.sidebar.button("Search"):
        st.experimental_set_query_params(search_input=search_query)  # Update the query parameters
    
    if search_query:
        # Perform search and display results
        results = search_index(index_dir, search_query)
        
        if results:
            st.subheader("Search Results")
            for result in results:
                file_name = os.path.basename(result["file_path"])  # Extract the file name
                highlighted_paragraph = highlight_query_terms(result["paragraph"], search_query)
                
                st.write("File:", file_name)
                st.write("Page:", result["page_number"])
                st.write("Paragraph:")
                st.markdown(highlighted_paragraph, unsafe_allow_html=True)  # Display highlighted paragraph
                st.write("---")
        else:
            st.write("No results found.")

if __name__ == "__main__":
    main()
