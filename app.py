# app.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import pandas as pd
import json
import time
import uuid
from datetime import datetime

from agents import AgentManager
from utils.logger import logger, performance_tracker
from utils.config import config_manager
from utils.export_manager import export_manager
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Initialize session state
if 'agent_manager' not in st.session_state:
    st.session_state.agent_manager = AgentManager(max_retries=2, verbose=True)
if 'results_history' not in st.session_state:
    st.session_state.results_history = []

def main():
    st.set_page_config(
        page_title="Enhanced Multi-Agent AI System", 
        layout="wide",
        page_icon="🧠",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .success-box {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 0.25rem;
            padding: 1rem;
            margin: 1rem 0;
        }
        .error-box {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 0.25rem;
            padding: 1rem;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<h1 class="main-header">🧠 Enhanced Multi-Agent AI System</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        available_models = config_manager.get_app_config().available_models
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            index=0 if config_manager.get_app_config().default_model in available_models 
            else 0
        )
        
        # Performance monitoring toggle
        enable_metrics = st.checkbox(
            "Enable Performance Monitoring", 
            value=config_manager.get_app_config().enable_metrics
        )
        
        # Export format
        export_format = st.selectbox(
            "Default Export Format",
            ["JSON", "PDF", "DOCX", "CSV"],
            index=0
        )
        
        st.markdown("---")
        
        # System metrics
        if enable_metrics:
            st.subheader("📊 System Metrics")
            metrics = performance_tracker.get_metrics()
            
            if metrics["agent_executions"]:
                total_executions = sum(metrics["agent_executions"].values())
                st.metric("Total Executions", total_executions)
                
                if metrics["avg_execution_times"]:
                    avg_time = sum(metrics["avg_execution_times"].values()) / len(metrics["avg_execution_times"])
                    st.metric("Avg Execution Time", f"{avg_time:.2f}s")

    # Main navigation
    selected_tab = option_menu(
        menu_title=None,
        options=["Medical Summarization", "Article Writing", "Data Sanitization", "Clinical Parser", "Performance Analytics", "Settings"],
        icons=["file-text", "pen", "shield-check", "clipboard-data", "graph-up", "gear"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#02ab21"},
        }
    )

    # Main content based on selected tab
    if selected_tab == "Medical Summarization":
        medical_summarization_section()
    elif selected_tab == "Article Writing":
        article_writing_section()
    elif selected_tab == "Data Sanitization":
        data_sanitization_section()
    elif selected_tab == "Clinical Parser":
        clinical_parser_section()
    elif selected_tab == "Performance Analytics":
        performance_analytics_section()
    elif selected_tab == "Settings":
        settings_section()

def medical_summarization_section():
    st.header("📄 Medical Text Summarization")
    st.write("Generate concise summaries of lengthy medical documents with AI-powered analysis.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        text = st.text_area(
            "Enter medical text to summarize:",
            height=200,
            placeholder="Paste your medical text here..."
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            summarize_btn = st.button("🔍 Summarize", type="primary", use_container_width=True)
        with col_btn2:
            if st.session_state.get('last_summary_result'):
                export_btn = st.button("💾 Export Results", use_container_width=True)
                if export_btn:
                    export_results(st.session_state.last_summary_result, "medical_summary")
    
    with col2:
        st.subheader("Configuration")
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.number_input("Max Tokens", 100, 1000, 300, 50)
        include_validation = st.checkbox("Include Validation", True)
    
    if summarize_btn and text:
        operation_id = str(uuid.uuid4())
        
        with st.status("Processing medical text...", expanded=True) as status:
            try:
                st.write("🔄 Generating summary...")
                main_agent = st.session_state.agent_manager.get_agent("summarize")
                
                start_time = time.time()
                summary = main_agent.call_llama(
                    [
                        main_agent.prepare_system_message(),
                        {"role": "user", "content": f"Please provide a concise summary of the following medical text:\n\n{text}"}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    operation_id=operation_id
                )
                execution_time = time.time() - start_time
                
                result = {
                    "operation_id": operation_id,
                    "task": "Medical Summarization",
                    "input_text": text,
                    "summary": summary,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "parameters": {
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                }
                
                if include_validation:
                    st.write("✅ Validating summary...")
                    validator_agent = st.session_state.agent_manager.get_agent("summarize_validator")
                    validation = validator_agent.execute(original_text=text, summary=summary)
                    result["validation"] = validation
                
                status.update(label="✅ Summary completed!", state="complete", expanded=False)
                
                # Display results
                display_summary_results(result)
                
                # Store in session state and history
                st.session_state.last_summary_result = result
                st.session_state.results_history.append(result)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Summarization Error: {e}")

def article_writing_section():
    st.header("✍️ Research Article Writing & Refinement")
    st.write("Create and refine research articles with AI assistance and quality validation.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("Research Topic:", placeholder="Enter the main topic for your article...")
        outline = st.text_area("Article Outline (optional):", height=150, placeholder="Provide a structured outline...")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            write_btn = st.button("📝 Write & Refine Article", type="primary", use_container_width=True)
        with col_btn2:
            if st.session_state.get('last_article_result'):
                export_btn = st.button("💾 Export Article", use_container_width=True)
                if export_btn:
                    export_results(st.session_state.last_article_result, "research_article")
    
    with col2:
        st.subheader("Configuration")
        temperature = st.slider("Creativity", 0.0, 1.0, 0.8, 0.1)
        max_tokens = st.number_input("Max Tokens", 500, 2000, 800, 100)
        include_refinement = st.checkbox("Include Refinement", True)
        include_validation = st.checkbox("Include Validation", True)
    
    if write_btn and topic:
        operation_id = str(uuid.uuid4())
        
        with st.status("Writing research article...", expanded=True) as status:
            try:
                st.write("📝 Creating initial draft...")
                writer_agent = st.session_state.agent_manager.get_agent("write_article")
                
                start_time = time.time()
                draft = writer_agent.execute(topic, outline)
                
                result = {
                    "operation_id": operation_id,
                    "task": "Article Writing",
                    "topic": topic,
                    "outline": outline,
                    "draft": draft,
                    "timestamp": datetime.now().isoformat(),
                    "parameters": {
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                }
                
                if include_refinement:
                    st.write("✨ Refining article...")
                    refiner_agent = st.session_state.agent_manager.get_agent("refiner")
                    refined_article = refiner_agent.execute(draft)
                    result["refined_article"] = refined_article
                
                if include_validation:
                    st.write("✅ Validating article quality...")
                    validator_agent = st.session_state.agent_manager.get_agent("validator")
                    final_article = result.get("refined_article", draft)
                    validation = validator_agent.execute(topic=topic, article=final_article)
                    result["validation"] = validation
                
                execution_time = time.time() - start_time
                result["execution_time"] = execution_time
                
                status.update(label="✅ Article completed!", state="complete", expanded=False)
                
                # Display results
                display_article_results(result)
                
                # Store in session state and history
                st.session_state.last_article_result = result
                st.session_state.results_history.append(result)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Article Writing Error: {e}")

def data_sanitization_section():
    st.header("🛡️ Medical Data Sanitization")
    st.write("Remove Protected Health Information (PHI) from medical data while preserving clinical value.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        medical_data = st.text_area(
            "Enter medical data to sanitize:",
            height=200,
            placeholder="Paste medical data containing PHI here..."
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            sanitize_btn = st.button("🔒 Sanitize Data", type="primary", use_container_width=True)
        with col_btn2:
            if st.session_state.get('last_sanitization_result'):
                export_btn = st.button("💾 Export Results", use_container_width=True)
                if export_btn:
                    export_results(st.session_state.last_sanitization_result, "sanitized_data")
    
    with col2:
        st.subheader("Configuration")
        temperature = st.slider("Precision", 0.0, 1.0, 0.3, 0.1)
        max_tokens = st.number_input("Max Tokens", 200, 1000, 600, 50)
        include_validation = st.checkbox("Include Validation", True)
        
        st.info("💡 Lower temperature values provide more consistent PHI removal.")
    
    if sanitize_btn and medical_data:
        operation_id = str(uuid.uuid4())
        
        with st.status("Sanitizing medical data...", expanded=True) as status:
            try:
                st.write("🔍 Identifying and removing PHI...")
                main_agent = st.session_state.agent_manager.get_agent("sanitize_data")
                
                start_time = time.time()
                sanitized_data = main_agent.execute(medical_data)
                execution_time = time.time() - start_time
                
                result = {
                    "operation_id": operation_id,
                    "task": "Data Sanitization",
                    "original_data": medical_data,
                    "sanitized_data": sanitized_data,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "parameters": {
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                }
                
                if include_validation:
                    st.write("✅ Validating PHI removal...")
                    validator_agent = st.session_state.agent_manager.get_agent("sanitize_data_validator")
                    validation = validator_agent.execute(original_data=medical_data, sanitized_data=sanitized_data)
                    result["validation"] = validation
                
                status.update(label="✅ Sanitization completed!", state="complete", expanded=False)
                
                # Display results
                display_sanitization_results(result)
                
                # Store in session state and history
                st.session_state.last_sanitization_result = result
                st.session_state.results_history.append(result)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Sanitization Error: {e}")

def clinical_parser_section():
    st.header("🏥 Clinical Note Parser")
    st.write("Parse clinical notes and extract structured medical information with advanced AI analysis.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        clinical_note = st.text_area(
            "Enter clinical note to parse:",
            height=200,
            placeholder="Paste clinical note here for structured extraction..."
        )
        
        tab1, tab2, tab3 = st.tabs(["🔍 Full Analysis", "🏷️ Entity Extraction", "📋 Quick Summary"])
        
        with tab1:
            full_analysis_btn = st.button("📊 Full Clinical Analysis", type="primary", use_container_width=True)
        with tab2:
            entity_extraction_btn = st.button("🏷️ Extract Medical Entities", use_container_width=True)
        with tab3:
            quick_summary_btn = st.button("📋 Generate Medical Summary", use_container_width=True)
        
        if st.session_state.get('last_clinical_result'):
            export_btn = st.button("💾 Export Clinical Analysis", use_container_width=True)
            if export_btn:
                export_results(st.session_state.last_clinical_result, "clinical_analysis")
    
    with col2:
        st.subheader("Configuration")
        temperature = st.slider("Analysis Precision", 0.0, 1.0, 0.5, 0.1)
        max_tokens = st.number_input("Max Tokens", 300, 1500, 800, 50)
        include_validation = st.checkbox("Include Validation", True)
        
        st.info("🏥 Clinical parser extracts demographics, symptoms, diagnoses, medications, and treatment plans.")
    
    if clinical_note:
        clinical_agent = st.session_state.agent_manager.get_agent("clinical_parser")
        
        if full_analysis_btn:
            perform_clinical_analysis(clinical_note, clinical_agent, "full", include_validation, temperature, max_tokens)
        elif entity_extraction_btn:
            perform_clinical_analysis(clinical_note, clinical_agent, "entities", include_validation, temperature, max_tokens)
        elif quick_summary_btn:
            perform_clinical_analysis(clinical_note, clinical_agent, "summary", include_validation, temperature, max_tokens)

def perform_clinical_analysis(clinical_note, clinical_agent, analysis_type, include_validation, temperature, max_tokens):
    operation_id = str(uuid.uuid4())
    
    with st.status(f"Performing clinical {analysis_type} analysis...", expanded=True) as status:
        try:
            start_time = time.time()
            
            if analysis_type == "full":
                st.write("📊 Extracting structured clinical data...")
                parsed_data = clinical_agent.execute(clinical_note)
                result_key = "parsed_data"
                result_data = parsed_data
            elif analysis_type == "entities":
                st.write("🏷️ Extracting medical entities...")
                entities = clinical_agent.extract_medical_entities(clinical_note)
                result_key = "entities"
                result_data = entities
            else:  # summary
                st.write("📋 Generating medical summary...")
                summary = clinical_agent.generate_medical_summary(clinical_note)
                result_key = "medical_summary"
                result_data = summary
            
            execution_time = time.time() - start_time
            
            result = {
                "operation_id": operation_id,
                "task": f"Clinical {analysis_type.title()} Analysis",
                "clinical_note": clinical_note,
                result_key: result_data,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "analysis_type": analysis_type
                }
            }
            
            if include_validation and analysis_type == "full":
                st.write("✅ Validating clinical extraction...")
                validator_agent = st.session_state.agent_manager.get_agent("clinical_parser_validator")
                validation = validator_agent.execute(clinical_note, result_data)
                result["validation"] = validation
            
            status.update(label="✅ Clinical analysis completed!", state="complete", expanded=False)
            
            # Display results
            display_clinical_results(result, analysis_type)
            
            # Store in session state and history
            st.session_state.last_clinical_result = result
            st.session_state.results_history.append(result)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            logger.error(f"Clinical Analysis Error: {e}")

def performance_analytics_section():
    st.header("📊 Performance Analytics")
    st.write("Monitor system performance, analyze agent metrics, and track usage patterns.")
    
    metrics = performance_tracker.get_metrics()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Agent Execution Summary")
        if metrics["agent_executions"]:
            executions_df = pd.DataFrame(
                list(metrics["agent_executions"].items()),
                columns=["Agent", "Executions"]
            )
            fig_bar = px.bar(executions_df, x="Agent", y="Executions", title="Agent Usage")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No execution data available yet.")
    
    with col2:
        st.subheader("Success Rates")
        if metrics["success_rates"]:
            success_data = []
            for agent, data in metrics["success_rates"].items():
                rate = data["success"] / data["total"] if data["total"] > 0 else 0
                success_data.append({"Agent": agent, "Success Rate": rate * 100})
            
            success_df = pd.DataFrame(success_data)
            fig_success = px.bar(success_df, x="Agent", y="Success Rate", title="Success Rates (%)")
            st.plotly_chart(fig_success, use_container_width=True)
        else:
            st.info("No success rate data available yet.")
    
    # Execution times
    st.subheader("Execution Time Analysis")
    if metrics["avg_execution_times"]:
        time_df = pd.DataFrame(
            list(metrics["avg_execution_times"].items()),
            columns=["Agent", "Avg Time (seconds)"]
        )
        fig_time = px.line(time_df, x="Agent", y="Avg Time (seconds)", title="Average Execution Times")
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No execution time data available yet.")
    
    # Results history
    st.subheader("Recent Operations History")
    if st.session_state.results_history:
        history_data = []
        for result in st.session_state.results_history[-10:]:  # Last 10 operations
            history_data.append({
                "Task": result["task"],
                "Timestamp": result["timestamp"],
                "Execution Time": f"{result.get('execution_time', 0):.2f}s",
                "Operation ID": result["operation_id"][:8] + "..."
            })
        
        history_df = pd.DataFrame(history_data)
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No operation history available yet.")
    
    # Export metrics
    if st.button("📊 Export Performance Report"):
        metrics_report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "recent_operations": st.session_state.results_history[-20:] if st.session_state.results_history else []
        }
        export_results(metrics_report, "performance_report")

def settings_section():
    st.header("⚙️ System Settings")
    st.write("Configure system parameters, manage agents, and adjust performance settings.")
    
    tab1, tab2, tab3 = st.tabs(["🎛️ General Settings", "🤖 Agent Configuration", "📁 Data Management"])
    
    with tab1:
        st.subheader("Application Settings")
        
        app_config = config_manager.get_app_config()
        
        # Model settings
        st.write("**Model Configuration**")
        default_model = st.selectbox(
            "Default Model",
            app_config.available_models,
            index=app_config.available_models.index(app_config.default_model)
        )
        
        # Theme settings
        theme = st.selectbox(
            "UI Theme",
            ["light", "dark"],
            index=0 if app_config.theme == "light" else 1
        )
        
        # Export settings
        export_format = st.selectbox(
            "Default Export Format",
            ["json", "pdf", "docx", "csv"],
            index=0
        )
        
        # Performance settings
        enable_metrics = st.checkbox(
            "Enable Performance Monitoring",
            value=app_config.enable_metrics
        )
        
        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1 if app_config.log_level == "INFO" else 0
        )
        
        if st.button("💾 Save General Settings"):
            app_config.default_model = default_model
            app_config.theme = theme
            app_config.export_format = export_format
            app_config.enable_metrics = enable_metrics
            app_config.log_level = log_level
            config_manager.update_app_config(app_config)
            st.success("✅ Settings saved successfully!")
    
    with tab2:
        st.subheader("Agent Configuration")
        
        agent_name = st.selectbox(
            "Select Agent to Configure",
            st.session_state.agent_manager.get_agent_list()
        )
        
        if agent_name:
            agent_config = config_manager.get_agent_config(agent_name.replace("_validator", "").replace("_agent", ""))
            
            col1, col2 = st.columns(2)
            
            with col1:
                temperature = st.slider(
                    "Temperature",
                    0.0, 1.0, agent_config.temperature, 0.1,
                    key=f"temp_{agent_name}"
                )
                max_tokens = st.number_input(
                    "Max Tokens",
                    100, 2000, agent_config.max_tokens, 50,
                    key=f"tokens_{agent_name}"
                )
                max_retries = st.number_input(
                    "Max Retries",
                    1, 10, agent_config.max_retries, 1,
                    key=f"retries_{agent_name}"
                )
            
            with col2:
                model = st.selectbox(
                    "Model",
                    config_manager.get_app_config().available_models,
                    index=config_manager.get_app_config().available_models.index(agent_config.model),
                    key=f"model_{agent_name}"
                )
                timeout = st.number_input(
                    "Timeout (seconds)",
                    10, 300, agent_config.timeout, 10,
                    key=f"timeout_{agent_name}"
                )
            
            system_prompt = st.text_area(
                "System Prompt",
                value=agent_config.system_prompt,
                height=100,
                key=f"prompt_{agent_name}"
            )
            
            if st.button(f"💾 Save {agent_name} Configuration"):
                from utils.config import AgentConfig
                new_config = AgentConfig(
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model,
                    system_prompt=system_prompt,
                    max_retries=max_retries,
                    timeout=timeout
                )
                config_manager.update_agent_config(agent_name.replace("_validator", "").replace("_agent", ""), new_config)
                st.success(f"✅ {agent_name} configuration saved successfully!")
    
    with tab3:
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Export Management**")
            if st.button("📊 Export All Configurations"):
                config_data = config_manager.to_dict()
                export_results(config_data, "system_configuration")
            
            if st.button("📋 Export Results History"):
                if st.session_state.results_history:
                    export_results({"results_history": st.session_state.results_history}, "results_history")
                else:
                    st.warning("No results history to export.")
        
        with col2:
            st.write("**System Maintenance**")
            if st.button("🗑️ Clear Results History"):
                st.session_state.results_history = []
                st.success("✅ Results history cleared!")
            
            if st.button("🔄 Reset Performance Metrics"):
                performance_tracker.metrics = {
                    "agent_executions": {},
                    "execution_times": {},
                    "token_usage": {},
                    "success_rates": {},
                    "system_metrics": {}
                }
                st.success("✅ Performance metrics reset!")

def display_summary_results(result):
    st.subheader("📄 Summary Results")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Generated Summary:**")
        st.markdown(f'<div class="success-box">{result["summary"]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.metric("Execution Time", f"{result['execution_time']:.2f}s")
        st.metric("Input Length", f"{len(result['input_text'])} chars")
        st.metric("Summary Length", f"{len(result['summary'])} chars")
        
        compression_ratio = len(result['summary']) / len(result['input_text'])
        st.metric("Compression Ratio", f"{compression_ratio:.2%}")
    
    if "validation" in result:
        st.subheader("✅ Validation Results")
        st.write(result["validation"])

def display_article_results(result):
    st.subheader("📝 Article Results")
    
    tabs = ["📄 Draft", "✨ Refined Article", "✅ Validation"] if "refined_article" in result else ["📄 Draft", "✅ Validation"]
    
    if "refined_article" in result:
        tab1, tab2, tab3 = st.tabs(tabs)
    else:
        tab1, tab2 = st.tabs(tabs[:2])
    
    with tab1:
        st.markdown("**Initial Draft:**")
        st.markdown(f'<div class="success-box">{result["draft"]}</div>', unsafe_allow_html=True)
    
    if "refined_article" in result:
        with tab2:
            st.markdown("**Refined Article:**")
            st.markdown(f'<div class="success-box">{result["refined_article"]}</div>', unsafe_allow_html=True)
        
        if "validation" in result:
            with tab3:
                st.markdown("**Validation Results:**")
                st.write(result["validation"])
    elif "validation" in result:
        with tab2:
            st.markdown("**Validation Results:**")
            st.write(result["validation"])
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Execution Time", f"{result['execution_time']:.2f}s")
    with col2:
        st.metric("Draft Length", f"{len(result['draft'])} chars")
    with col3:
        if "refined_article" in result:
            st.metric("Final Length", f"{len(result['refined_article'])} chars")

def display_sanitization_results(result):
    st.subheader("🛡️ Sanitization Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Original Data:**")
        st.text_area("Original", result["original_data"], height=150, disabled=True)
    
    with col2:
        st.markdown("**Sanitized Data:**")
        st.text_area("Sanitized", result["sanitized_data"], height=150, disabled=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Execution Time", f"{result['execution_time']:.2f}s")
    with col2:
        st.metric("Original Length", f"{len(result['original_data'])} chars")
    with col3:
        st.metric("Sanitized Length", f"{len(result['sanitized_data'])} chars")
    
    if "validation" in result:
        st.subheader("✅ Validation Results")
        st.write(result["validation"])

def display_clinical_results(result, analysis_type):
    st.subheader("🏥 Clinical Analysis Results")
    
    if analysis_type == "full":
        display_structured_clinical_data(result["parsed_data"])
    elif analysis_type == "entities":
        display_medical_entities(result["entities"])
    else:  # summary
        st.markdown("**Medical Summary:**")
        st.markdown(f'<div class="success-box">{result["medical_summary"]}</div>', unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Execution Time", f"{result['execution_time']:.2f}s")
    with col2:
        st.metric("Note Length", f"{len(result['clinical_note'])} chars")
    with col3:
        if analysis_type == "full" and "metadata" in result["parsed_data"]:
            confidence = result["parsed_data"]["metadata"].get("confidence_score", "N/A")
            st.metric("Confidence", confidence)
    
    if "validation" in result:
        st.subheader("✅ Validation Results")
        st.json(result["validation"])

def display_structured_clinical_data(parsed_data):
    sections = ["demographics", "chief_complaint", "present_illness", "medical_history", 
               "medications", "allergies", "vital_signs", "physical_exam", "assessment", "plan"]
    
    cols = st.columns(2)
    col_idx = 0
    
    for section in sections:
        if section in parsed_data and parsed_data[section]:
            with cols[col_idx % 2]:
                st.markdown(f"**{section.replace('_', ' ').title()}:**")
                if isinstance(parsed_data[section], list):
                    for item in parsed_data[section]:
                        if item and item != "Not mentioned":
                            st.write(f"• {item}")
                else:
                    st.write(parsed_data[section])
                st.markdown("---")
            col_idx += 1

def display_medical_entities(entities):
    cols = st.columns(len(entities))
    
    for idx, (category, items) in enumerate(entities.items()):
        with cols[idx]:
            st.markdown(f"**{category.title()}:**")
            if items:
                for item in items:
                    st.write(f"• {item}")
            else:
                st.write("None identified")

def export_results(data, result_type):
    try:
        format_type = config_manager.get_app_config().export_format.lower()
        
        if format_type == "json":
            filepath = export_manager.export_to_json(data, f"{result_type}.json")
        elif format_type == "pdf":
            filepath = export_manager.export_to_pdf(data, f"{result_type.replace('_', ' ').title()}")
        elif format_type == "docx":
            filepath = export_manager.export_to_docx(data, f"{result_type.replace('_', ' ').title()}")
        elif format_type == "csv":
            filepath = export_manager.export_to_csv(data, f"{result_type}.csv")
        
        # Provide download
        with open(filepath, 'rb') as f:
            st.download_button(
                label=f"📥 Download {format_type.upper()}",
                data=f.read(),
                file_name=filepath.split('/')[-1],
                mime=f"application/{format_type}"
            )
        
        st.success(f"✅ Results exported successfully as {format_type.upper()}!")
        
    except Exception as e:
        st.error(f"❌ Export failed: {str(e)}")

if __name__ == "__main__":
    main()
