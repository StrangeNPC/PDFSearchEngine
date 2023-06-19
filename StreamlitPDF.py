import os
import re
import streamlit as st
import base64
from PyPDF2 import PdfReader, PdfWriter
from whoosh import fields, index
from whoosh.qparser import QueryParser
from whoosh.index import create_in, open_dir
from whoosh.filedb.filestore import RamStorage


def create_index(directory):
    schema = fields.Schema(
        file_path=fields.TEXT(stored=True),
        page_number=fields.NUMERIC(stored=True),
        content=fields.TEXT(stored=True),
    )

    if not os.path.exists(directory):
        os.makedirs(directory)

    ix = create_in(directory, schema)
    writer = ix.writer()

    # Index the PDF files
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "rb") as file:
                pdf = PdfReader(file)

                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text().replace("\n", " ")

                    writer.add_document(
                        file_path=file_path,
                        page_number=page_num + 1,
                        content=text,
                    )
                    st.write("Indexed:", file_path, "Page:", page_num + 1)

    writer.commit()
    return ix


def search_index(index_dir, search_query, selected_documents):
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

            if matched_paragraph and os.path.basename(file_path) in selected_documents:
                result = {
                    "file_path": file_path,
                    "page_number": page_number,
                    "paragraph": matched_paragraph,
                }
                results.append(result)
    return results


def highlight_query_terms(paragraph, query):
    highlighted_paragraph = re.sub(
        fr"\b({re.escape(query)})\b",
        r'<mark style="background-color: yellow;">\1</mark>',
        paragraph,
        flags=re.IGNORECASE,
    )
    return highlighted_paragraph


# Download function
def download_page(file_path, page_number):
    with open(file_path, "rb") as file:
        pdf = PdfReader(file)
        output_path = f"download_page_{os.path.basename(file_path)}_page_{page_number}.pdf"
        output_pdf = PdfWriter()
        output_pdf.add_page(pdf.pages[page_number - 1])
        with open(output_path, "wb") as output_file:
            output_pdf.write(output_file)
        return output_path


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

    # Checkbox for document selection
    selected_documents = st.sidebar.multiselect(
        "Select Documents to Search",
        [os.path.basename(doc) for doc in os.listdir(index_dir) if doc.endswith(".pdf")],
    )

    search_query = placeholder.text_input("Enter search query", key="search_input")

    if st.sidebar.button("Search"):
        st.experimental_set_query_params(search_input=search_query)  # Update the query parameters
        results = search_index(index_dir, search_query, selected_documents)  # Update the results based on selected documents
        st.session_state.selected_documents = selected_documents  # Store the selected documents in session state

    if search_query:
        # Perform search and display results
        results = search_index(index_dir, search_query, selected_documents)

        if results:
            st.subheader("Search Results")
            for result in results:
                file_name = os.path.basename(result["file_path"])  # Extract the file name
                highlighted_paragraph = highlight_query_terms(result["paragraph"], search_query)

                st.write("File:", file_name)
                st.write("Page:", result["page_number"])
                st.write("Paragraph:")
                st.markdown(highlighted_paragraph, unsafe_allow_html=True)  # Display highlighted paragraph

                # Download button
                download_button_label = f"Download Page {result['page_number']}"
                if st.button(download_button_label):
                    download_path = download_page(result["file_path"], result["page_number"])
                    st.write("Downloading...")
                    st.markdown(
                        get_download_link(download_path, download_button_label),
                        unsafe_allow_html=True,
                    )

                st.write("---")
        else:
            st.write("No results found.")


# Function to generate a download link
def get_download_link(file_path, text):
    with open(file_path, "rb") as file:
        data = file.read()
    base64_data = base64.b64encode(data).decode("utf-8")
    download_link = f'<a href="data:application/octet-stream;base64,{base64_data}" download="{file_path}">{text}</a>'
    return download_link


if __name__ == "__main__":
    main()

