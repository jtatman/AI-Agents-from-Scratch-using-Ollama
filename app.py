# app.py

import streamlit as st
from agents import AgentManager
import os
from dotenv import load_dotenv
import logging
from utils.logger import logger


# Load environment variables from .env if present
load_dotenv()

def main():
    st.set_page_config(page_title="Multi-Agent AI System", layout="wide")
    st.title("Multi-Agent AI System with Collaboration and Validation")

    st.sidebar.title("Select Task")
    task = st.sidebar.selectbox("Choose a task:", [
        "Summarize Scientific Text",
        "Write and Refine Research Article",
        "Search arXiv Papers",
        "Search Google Scholar",
        "Search Scholarly Web"
    ])

    agent_manager = AgentManager()

    if task == "Summarize Medical Text":
        summarize_section(agent_manager)
    elif task == "Write and Refine Research Article":
        write_and_refine_article_section(agent_manager)
    elif task == "Search arXiv Papers":
        search_arxiv_papers(agent_manager)
    elif task == "Search Google Scholar":
        search_google_scholar(agent_manager)
    elif task == "Search Scholarly Web":
        search_web(agent_manager)
    #elif task == "Sanitize Medical Data (PHI)":
    #    sanitize_data_section(agent_manager)

def summarize_section(agent_manager):
    st.header("Summarize Scientific Papers")
    paper_text = st.text_area("Enter scientific paper text to summarize:", height=200)
    if st.button("Summarize"):
        if paper_text:
            main_agent = agent_manager.get_agent("summarize")
            validator_agent = agent_manager.get_agent("summarize_validator")
            with st.spinner("Summarizing..."):
                try:
                    summary = main_agent.execute(paper_text)
                    st.subheader("Summary:")
                    st.write(summary)
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.error(f"SummarizeAgent Error: {e}")
                    return

            with st.spinner("Validating summary..."):
                try:
                    validation = validator_agent.execute(original_text=paper_text, summary=summary)
                    st.subheader("Validation:")
                    st.write(validation)
                except Exception as e:
                    st.error(f"Validation Error: {e}")
                    logger.error(f"SummarizeValidatorAgent Error: {e}")
        else:
            st.warning("Please enter some text to summarize.")

def write_and_refine_article_section(agent_manager):
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
                    draft = writer_agent.execute(topic, outline)
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
def search_arxiv_papers(agent_manager):
    st.header("Search arXiv Papers")
    query = st.text_input("Enter search query for arXiv:")
    if st.button("Search arXiv"):
        if query:
            arxiv_agent = agent_manager.get_agent("arxiv")
            validator_agent = agent_manager.get_agent("arxiv_validator")
            with st.spinner("Searching arXiv..."):
                try:
                    results = arxiv_agent.search(query)
                    validated_results = validator_agent.validate(results)
                    st.subheader("Search Results:")
                    for result in validated_results:
                        st.write(f"**Title:** {result['title']}")
                        st.write(f"**Authors:** {', '.join(result['authors'])}")
                        st.write(f"**Summary:** {result['summary']}")
                        st.write(f"[Read more]({result['url']})")
                        st.write("---")
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.error(f"ArxivAgent Error: {e}")
        else:
            st.warning("Please enter a search query.")

def search_google_scholar(agent_manager):
    st.header("Search Google Scholar")
    query = st.text_input("Enter search query for Google Scholar:")
    if st.button("Search Google Scholar"):
        if query:
            google_scholar_agent = agent_manager.get_agent("google_scholar")
            validator_agent = agent_manager.get_agent("google_scholar_validator")
            with st.spinner("Searching Google Scholar..."):
                try:
                    results = google_scholar_agent.search(query)
                    validated_results = validator_agent.validate(results)
                    st.subheader("Search Results:")
                    for result in validated_results:
                        st.write(f"**Title:** {result['title']}")
                        st.write(f"**Authors:** {result['authors']}")
                        st.write(f"**Abstract:** {result['abstract']}")
                        st.write(f"[Read more]({result['url']})")
                        st.write("---")
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.error(f"GoogleScholarAgent Error: {e}")
        else:
            st.warning("Please enter a search query.")

def search_web(agent_manager):
    st.header("Search Scholarly Web")
    query = st.text_input("Enter search query for the web:")
    if st.button("Search Web"):
        if query:
            web_search_agent = agent_manager.get_agent("web_search")
            validator_agent = agent_manager.get_agent("web_search_validator")
            with st.spinner("Searching the web..."):
                try:
                    results = web_search_agent.search(query)
                    validated_results = validator_agent.validate(results)
                    st.subheader("Search Results:")
                    for result in validated_results:
                        st.write(f"**Title:** {result['title']}")
                        st.write(f"**Author:** {result['author']}")
                        st.write(f"**Abstract:** {result['abstract']}")
                        st.write(f"[Read more]({result['url']})")
                        st.write("---")
                except Exception as e:
                    st.error(f"Error: {e}")
                    logger.error(f"WebSearchAgent Error: {e}")
        else:
            st.warning("Please enter a search query.")

if __name__ == "__main__":
    main()
