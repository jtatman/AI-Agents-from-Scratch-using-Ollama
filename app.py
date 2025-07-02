# app.py

import streamlit as st
from agents import AgentManager
import os
from dotenv import load_dotenv
import logging
from utils.logger import logger
import requests
import PyPDF2 
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Optional
import arxiv
import scholarly
import itertools


# Load environment variables from .env if present
load_dotenv()

def get_ollama_models(server_address):
    """Fetches the list of models from the Ollama server."""
    try:
        response = requests.get(f"{server_address}/api/tags")
        response.raise_for_status()
        models_data = response.json()
        models = [ model['name'] for model in models_data['models'] ]
        return models
    except Exception as e:
        logger.error(f"Failed to fetch models from Ollama server: {e}")
        return []

def main():
    st.set_page_config(page_title="Multi-Agent AI System", layout="wide")
    st.title("Multi-Agent AI System with Collaboration and Validation")

    st.sidebar.title("Settings")
    server_address = st.sidebar.text_input("Ollama Server Address", value="http://localhost:11434")

    # Verify server connectivity and fetch models
    if st.sidebar.button("Verify Server"):
        try:
            models = get_ollama_models(server_address)
            if models:
                st.sidebar.success("Server connected successfully!")
            else:
                st.sidebar.warning("No models found on the server.")
        except Exception as e:
            st.sidebar.error(f"Failed to connect to server: {e}")

    # Populate the model dropdown dynamically
    models = get_ollama_models(server_address)
    model_name = st.sidebar.selectbox("Select Model", models if models else ["No models available"])

    st.sidebar.title("Select Task")
    task = st.sidebar.selectbox("Choose a task:", [
        "Search arXiv Papers",
        "Search Web",
        "Summarize Scientific Papers",
        "Write and Refine Research Article"
    ])

    agent_manager = AgentManager(max_retries=2, verbose=True)

    if task == "Search arXiv Papers":
        search_arxiv_papers()
    elif task == "Search Web":
        search_web()
    elif task == "Summarize Scientific Papers":
        summarize_section(agent_manager, server_address, model_name)
    elif task == "Write and Refine Research Article":
        write_and_refine_article_section(agent_manager, server_address, model_name)

def summarize_section(agent_manager: AgentManager, server_address: str, model_name: str) -> None:
    st.header("Summarize Scientific Papers")
    mode = st.radio("Choose input type:", ["URL (PDF or Web)", "Text", "Upload PDF"])

    # Use session_state for persistent extracted_text
    if "extracted_text" not in st.session_state:
        st.session_state["extracted_text"] = ""
    extracted_text = st.session_state["extracted_text"]

    # Extraction logic
    if mode == "URL (PDF or Web)":
        url = st.text_input("Enter the URL of the paper (PDF or web page):")
        if url and st.button("Extract"):
            st.session_state["extracted_text"] = ""  # Reset before extraction
            if url.lower().endswith(".pdf"):
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    with open("temp.pdf", "wb") as f:
                        f.write(response.content)
                    with open("temp.pdf", "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text
                    if not text.strip():
                        st.error("No extractable text found in the downloaded PDF. It may be scanned or image-based.")
                        logger.error("No extractable text found in the downloaded PDF.")
                    else:
                        st.session_state["extracted_text"] = text
                    os.remove("temp.pdf")
                except Exception as e:
                    st.error(f"Failed to extract from PDF: {e}")
                    logger.error(f"Failed to extract from PDF: {e}")
            else:
                try:
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, "html.parser")
                    abstract = soup.find("meta", {"name": "description"})
                    if isinstance(abstract, Tag):
                        text = abstract.get("content", "")
                    else:
                        text = soup.get_text()
                    st.session_state["extracted_text"] = text
                except Exception as e:
                    st.error(f"Failed to extract from web page: {e}")
                    logger.error(f"Failed to extract from web page: {e}")
        extracted_text = st.session_state["extracted_text"]

    elif mode == "Upload PDF":
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        if uploaded_file and st.button("Extract"):
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                if not text.strip():
                    st.error("No extractable text found in the uploaded PDF. It may be scanned or image-based.")
                else:
                    st.session_state["extracted_text"] = text
            except Exception as e:
                st.error(f"Failed to extract from uploaded PDF: {e}")
                logger.error(f"Failed to extract from uploaded PDF: {e}")
        extracted_text = st.session_state["extracted_text"]

    else:  # Text
        text = st.text_area("Paste your text here:", value=extracted_text)
        if text != extracted_text:
            st.session_state["extracted_text"] = text
        extracted_text = st.session_state["extracted_text"]

    # Summarization logic
    if extracted_text:
        if st.button("Summarize"):
            main_agent = agent_manager.get_agent("summarize")
            validator_agent = agent_manager.get_agent("summarize_validator")
            with st.spinner("Summarizing..."):
                try:
                    summary_result = main_agent.execute(extracted_text, server_address, model_name)
                    summary = summary_result.summary if hasattr(summary_result, 'summary') else summary_result
                    st.subheader("Summary:")
                    st.write(summary)
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.error(f"SummarizeAgent Error: {e}")
                    return
            with st.spinner("Validating summary..."):
                try:
                    validation = validator_agent.execute(original_text=extracted_text, summary=summary)
                    st.subheader("Validation:")
                    st.write(validation)
                except Exception as e:
                    st.error(f"Validation Error: {e}")
                    logger.error(f"SummarizeValidatorAgent Error: {e}")
    else:
        st.info("Please provide input and click 'Extract' (if needed) before summarizing.")


def write_and_refine_article_section(agent_manager: AgentManager, server_address: str, model_name: str) -> None:
    st.header("Write and Refine Research Article")
    topic = st.text_input("Enter the topic for the research article:")
    outline = st.text_area("Enter an outline (optional):", height=150)
    if st.button("Write and Refine Article"):
        if topic:
            writer_agent = agent_manager.get_agent("write_article")
            refiner_agent = agent_manager.get_agent("refiner")
            validator_agent = agent_manager.get_agent("validator")
            with st.spinner("Writing article..."):
                try:
                    draft_result = writer_agent.execute(topic, outline)
                    draft = draft_result.article if hasattr(draft_result, 'article') else draft_result
                    st.subheader("Draft Article:")
                    st.write(draft)
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.error(f"WriteArticleAgent Error: {e}")
                    return

            with st.spinner("Refining article..."):
                try:
                    refined_article = refiner_agent.execute(draft)
                    st.subheader("Refined Article:")
                    st.write(refined_article)
                except Exception as e:
                    st.error(f"Refinement Error: {e}")
                    logger.error(f"RefinerAgent Error: {e}")
                    return

            with st.spinner("Validating article..."):
                try:
                    validation = validator_agent.execute(topic=topic, article=refined_article)
                    st.subheader("Validation:")
                    st.write(validation)
                except Exception as e:
                    st.error(f"Validation Error: {e}")
                    logger.error(f"ValidatorAgent Error: {e}")
        else:
            st.warning("Please enter a topic for the research article.")


# new functions that need agent configuration
def search_arxiv_papers() -> None:
    st.header("Search arXiv Papers")
    query = st.text_input("Enter search query for arXiv:")
    if st.button("Search arXiv"):
        if query:
            try:
                search = arxiv.Search(
                    query=query,
                    max_results=10,
                    sort_by=arxiv.SortCriterion.Relevance
                )
                results = []
                for result in search.results():
                    summary = getattr(result, 'summary', None)
                    authors = [author.name for author in getattr(result, 'authors', [])] if hasattr(result, 'authors') else None
                    if not summary or not authors:
                        continue
                    title = getattr(result, 'title', str(result))
                    url = getattr(result, 'entry_id', '')
                    results.append({'title': title, 'summary': summary, 'authors': authors, 'url': url})
                st.subheader("Search Results:")
                for result in results:
                    with st.container():
                        st.markdown(f"### [{result['title']}]({result['url']})")
                        st.write(f"**Authors:** {', '.join(result['authors'])}")
                        st.write(f"**Summary:** {result['summary']}")
                        st.write(f"[Read more]({result['url']})")
                        st.write("---")
            except Exception as e:
                st.error(f"Error: {e}")
                logger.error(f"arXiv search error: {e}")
        else:
            st.warning("Please enter a search query.")

def search_web() -> None:
    st.header("Search Web")
    query = st.text_input("Enter search query for the web:")
    api_key = st.secrets["SERPER_API_KEY"] if "SERPER_API_KEY" in st.secrets else st.text_input("Enter Serper API Key:")
    # Use sidebar-selected model and server, fallback to string defaults if None
    server_address = st.session_state.get('server_address') or "http://localhost:11434"
    model_name = st.session_state.get('model_name') or "deepseek-r1:1.5b"
    if st.button("Search Web"):
        if query and api_key:
            from agents.web_search_agent import WebSearchAgent
            from agents.web_search_validator_agent import WebSearchValidatorAgent
            with st.spinner("Searching the web and validating results..."):
                try:
                    search_agent = WebSearchAgent(api_key=api_key, backend="serper", max_results=10)
                    validator_agent = WebSearchValidatorAgent(model_name=str(model_name), server_address=str(server_address), max_results=10)
                    results = search_agent.search(query)
                    validated_results = validator_agent.validate(results)
                    st.subheader("Search Results:")
                    for result in validated_results:
                        st.markdown(f"### [{result.get('title','')}]({result.get('url','')})")
                        st.write(f"**Snippet:** {result.get('snippet','')}")
                        st.write(f"**Source:** {result.get('source','web')}")
                        st.write("---")
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.error(f"WebSearchAgent/Validator Error: {e}")
        else:
            st.warning("Please enter a search query and API key.")

    # --- Sidebar: View Citations ---
    if "citations" in st.session_state and st.session_state["citations"]:
        with st.sidebar.expander("View Citations", expanded=False):
            st.markdown("**Collected Citations:**")
            for i, citation in enumerate(st.session_state["citations"]):
                st.code(citation, language="text")
            st.download_button(
                label="Download All Citations (txt)",
                data="\n\n".join(st.session_state["citations"]),
                file_name="citations.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
