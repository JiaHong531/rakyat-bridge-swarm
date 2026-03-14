import streamlit as st
import sys
import io
import contextlib
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.swarm import RakyatSwarm

# --- Page Config ---
st.set_page_config(page_title="RakyatBridge Swarm", page_icon="🌉", layout="wide")
st.title("🌉 RakyatBridge: Public Services Swarm")
st.markdown("**Track A Submission** | Multilingual Agentic Recovery & Retrieval")

# --- Sidebar: Architecture Info ---
with st.sidebar:
    st.header("🏗️ System Architecture")
    st.markdown("""
    **Agents:**
    - 🛡️ Agent 0: Guardrail (Safety)
    - 🗣️ Agent 1A: Linguist (Dialect → Formal)
    - 🔍 Agent 2: Researcher (MCP Policy Search)
    - 📝 Agent 3: Simplifier (5th-grade)
    - 🔄 Agent 1B: Linguist Reverse (Formal → Dialect)

    **MCP Tools:**
    - 📖 `tool_dictionary_lookup`
    - 📋 `tool_policy_search`

    **Safety Layers:**
    - ✅ Rule-based keyword filter
    - ✅ LLM semantic classifier
    - ✅ Fail-safe on parse error
    """)
    st.divider()
    st.caption("Powered by Gemini · Google GenAI SDK")

# --- Initialize Swarm & Session State ---
@st.cache_resource
def get_swarm():
    return RakyatSwarm()

swarm = get_swarm()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_traces" not in st.session_state:
    st.session_state.last_traces = ""
if "last_verdict" not in st.session_state:
    st.session_state.last_verdict = None

# --- UI Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Citizen Chat")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question in local dialect (e.g., 'Tok wan saya uzur...')"):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Swarm is reasoning..."):
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    try:
                        final_answer = swarm.run_workflow(prompt)
                    except Exception as e:
                        final_answer = f"System Error: {str(e)}"

                traces = f.getvalue()

            st.session_state.last_traces = traces

            # ✅ Show blocked banner if guardrail triggered
            if "⚠️" in final_answer:
                st.error(final_answer)
            else:
                st.markdown(final_answer)

            st.session_state.messages.append({"role": "assistant", "content": final_answer})

with col2:
    st.subheader("🧠 Agent Reasoning Traces")
    st.markdown("*Live A2A and MCP Server Logs*")

    if st.session_state.last_traces:
        # ✅ Highlight blocked queries in traces
        trace_text = st.session_state.last_traces
        if "BLOCKED" in trace_text:
            st.warning("⚠️ Guardrail triggered on last query")

        st.code(trace_text, language="log")

        if st.button("🗑️ Clear Traces"):
            st.session_state.last_traces = ""
            st.rerun()
    else:
        st.info("Awaiting query to begin reasoning traces...")

    # ✅ Safety status indicator
    st.divider()
    st.subheader("🛡️ Safety Status")
    if st.session_state.last_traces:
        if "BLOCKED" in st.session_state.last_traces:
            st.error("🚨 Last query: BLOCKED")
        elif "Input cleared" in st.session_state.last_traces:
            st.success("✅ Last query: SAFE")
        else:
            st.info("ℹ️ Awaiting classification")
    else:
        st.info("No queries yet")