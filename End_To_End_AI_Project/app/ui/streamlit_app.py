"""
ui/streamlit_app.py — Streamlit Web Interface
===============================================


This is the layer that turns your backend pipeline into a product.

Why Streamlit?
  - Zero frontend knowledge needed (Python only)
  - Looks professional instantly
  - Great for portfolios and demos
  - Used in real AI teams for internal tools

What this UI provides:
  - Chat interface with message history
  - Sidebar with session stats and tool usage
  - Conversation export as JSON
  - Transparent tool usage display
  - New session button

Run with:
  streamlit run app/ui/streamlit_app.py
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from app.router import route_query
from app.state import AssistantState
from app.validator import validate_response
from app.conversation import ConversationManager
from app.utils.config import load_config
from app.utils.logger import get_logger

logger = get_logger(__name__)


def init_session():
    """Initialise Streamlit session state on first load."""
    if "conversation" not in st.session_state:
        st.session_state.conversation = ConversationManager(max_context_turns=5)
    if "messages" not in st.session_state:
        st.session_state.messages = []


def run_pipeline(user_query: str) -> str:
    """
    Run the full AI pipeline for a user query.
    Returns the final response string.
    """
    state = AssistantState(user_query=user_query)
    conversation = st.session_state.conversation

    # Inject conversation context into routing
    context = conversation.get_context_for_routing()
    result = route_query(user_query, state, conversation_context=context)

    # Validate
    validated = validate_response(result, state)

    # Record the turn
    conversation.add_turn(
        user_query=user_query,
        routing_decision=state.routing_decision,
        tool_used=state.tool_used,
        tool_output=state.tool_output,
        assistant_response=validated.final_response,
        is_valid=validated.is_valid,
        error=state.error,
    )

    return validated.final_response, state.tool_used


def inject_style():
    """Inject custom styles for a modern chat UI."""
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        .stApp {
            min-height: 100vh;
            background: radial-gradient(circle at top left, #0f172a 0%, transparent 40%),
                        radial-gradient(circle at bottom right, #111827 0%, transparent 32%),
                        linear-gradient(180deg, #020617 0%, #0f172a 100%);
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            border-radius: 1rem;
            backdrop-filter: blur(16px);
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .stSidebar {
            background: rgba(15, 23, 42, 0.92);
            border-radius: 1rem;
            padding: 1.25rem 1rem;
        }

        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #f8fafc;
        }

        .stChatMessage [data-testid='stMarkdownContainer'] {
            font-size: 1rem;
            line-height: 1.75;
        }

        .stChatMessage:nth-of-type(odd) {
            background: rgba(15, 23, 42, 0.88);
            border-left: 4px solid #38bdf8;
            padding: 1rem;
            border-radius: 1.2rem;
        }

        .stChatMessage:nth-of-type(even) {
            background: rgba(30, 58, 138, 0.9);
            border-left: 4px solid #60a5fa;
            padding: 1rem;
            border-radius: 1.2rem;
        }

        .stButton button, .stDownloadButton button {
            background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 0.85rem !important;
            padding: 0.85rem 1rem !important;
            box-shadow: 0 14px 30px rgba(8, 145, 178, 0.18) !important;
        }

        .stButton button:hover, .stDownloadButton button:hover {
            opacity: 0.96;
        }

        footer, header, #MainMenu {
            visibility: hidden;
        }

        .welcome-card {
            border-radius: 1.5rem;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.5rem;
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.06);
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.25);
        }

        .welcome-card h2 {
            margin-bottom: 0.35rem;
        }

        .feature-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.55rem 0.9rem;
            border-radius: 999px;
            background: rgba(99, 102, 241, 0.18);
            color: #e0f2fe;
            margin-right: 0.6rem;
            margin-bottom: 0.6rem;
            font-size: 0.94rem;
            border: 1px solid rgba(99, 102, 241, 0.14);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render the sidebar with session stats and controls."""
    conversation = st.session_state.conversation

    st.sidebar.title("🤖 AI Assistant")
    st.sidebar.markdown("#### Smart, fast, and transparent conversation")
    st.sidebar.divider()

    # Session stats
    st.sidebar.markdown("### 📊 Session Stats")
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Turns", conversation.get_turn_count())
    col2.metric("Success", f"{conversation.get_success_rate()}%")

    # Tool usage breakdown
    tool_freq = conversation.get_tool_frequency()
    if tool_freq:
        st.sidebar.markdown("### 🔧 Tools Used")
        for tool, count in sorted(tool_freq.items(), key=lambda x: -x[1]):
            emoji = {"calculator": "🧮", "weather": "🌤️", "wikipedia": "📖", "converter": "📏"}.get(tool, "🔧")
            st.sidebar.markdown(f"{emoji} **{tool}** — {count}x")

    st.sidebar.divider()

    # Available tools
    st.sidebar.markdown("### 💡 Quick prompts")
    st.sidebar.markdown(
        "- **What's 25% of 480?**  \n"
        "- **Weather in Tokyo?**  \n"
        "- **Tell me about BERT**  \n"
        "- **Convert 100F to Celsius**  \n"
        "- **What did I ask first?**"
    )

    st.sidebar.divider()

    # Controls
    col_a, col_b = st.sidebar.columns(2)
    if col_a.button("🗑️ New Session", use_container_width=True):
        st.session_state.conversation = ConversationManager()
        st.session_state.messages = []
        st.rerun()

    if col_b.button("📥 Export JSON", use_container_width=True):
        json_export = conversation.export_json()
        st.sidebar.download_button(
            label="Download",
            data=json_export,
            file_name="conversation_export.json",
            mime="application/json",
        )


def main():
    """Main Streamlit app entry point."""
    st.set_page_config(
        page_title="AI Assistant",
        page_icon="🤖",
        layout="wide",
    )

    inject_style()
    load_config()
    init_session()
    render_sidebar()

    st.markdown(
        """
        <div class='welcome-card'>
            <h2>AI Assistant</h2>
            <p style='color:#cbd5e1; font-size:1rem; margin-top:0.35rem;'>
                A polished conversational demo with tool-aware reasoning, validation, and export.
            </p>
            <div style='margin-top:1rem;'>
                <span class='feature-badge'>🧠 Context-aware</span>
                <span class='feature-badge'>⚡ Fast responses</span>
                <span class='feature-badge'>🔍 Tool transparent</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tool_used"):
                emoji = {"calculator": "🧮", "weather": "🌤️", "wikipedia": "📖", "converter": "📏"}.get(message["tool_used"], "🔧")
                st.caption(f"{emoji} Used tool: **{message['tool_used']}**")

    if user_input := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response, tool_used = run_pipeline(user_input)
                    st.markdown(response)
                    if tool_used:
                        emoji = {"calculator": "🧮", "weather": "🌤️", "wikipedia": "📖", "converter": "📏"}.get(tool_used, "🔧")
                        st.caption(f"{emoji} Used tool: **{tool_used}**")
                except Exception as e:
                    response = f"Something went wrong: {e}"
                    tool_used = None
                    st.error(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "tool_used": tool_used,
        })

        st.rerun()


if __name__ == "__main__":
    main()
