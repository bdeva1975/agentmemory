import streamlit as st
from agentmemory import AgentMemory

st.set_page_config(
    page_title="AgentMemory",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 AgentMemory")
st.caption("Persistent memory for your OpenAI agents — store, recall, and forget.")

st.divider()

# Initialise memory store in session
if "memory" not in st.session_state:
    st.session_state.memory = AgentMemory(memory_path="agent_memory.json")

memory = st.session_state.memory

# Sidebar — memory stats
with st.sidebar:
    st.header("📊 Memory Stats")
    st.metric("Total Memories", memory.count)
    if st.button("🗑️ Forget All", use_container_width=True, type="secondary"):
        memory.forget_all()
        st.success("All memories cleared.")
        st.rerun()
    st.divider()
    st.header("📋 All Memories")
    all_memories = memory.list_all()
    if all_memories:
        for m in all_memories:
            with st.expander(f"{m.category.upper()} — {m.content[:40]}..."):
                st.write(f"**Content:** {m.content}")
                st.write(f"**Category:** {m.category}")
                st.write(f"**Stored at:** {m.created_at}")
                if st.button("🗑️ Forget", key=m.id):
                    memory.forget(m.id)
                    st.rerun()
    else:
        st.info("No memories stored yet.")

# Main — Remember
st.subheader("💬 Remember")
st.caption("Paste any conversation message or text to extract and store memories.")

text_input = st.text_area(
    label="Text to remember",
    placeholder="e.g. I am building a RAG application using Python. I prefer concise answers.",
    height=120,
)

if st.button("🧠 Store Memories", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Extracting memories..."):
            stored = memory.remember(text_input)
        if stored:
            st.success(f"Stored {len(stored)} memories:")
            for m in stored:
                st.info(f"**{m.category.upper()}** — {m.content}")
            st.rerun()
        else:
            st.warning("No meaningful memories found in that text.")

st.divider()

# Main — Recall
st.subheader("🔍 Recall")
st.caption("Ask a question to retrieve relevant memories.")

query_input = st.text_input(
    label="Search query",
    placeholder="e.g. What is the user building?",
)

if st.button("🔍 Search Memories", use_container_width=True, type="primary"):
    if not query_input.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching memories..."):
            results = memory.recall(query_input)
        if results.memories:
            st.success(f"Found {results.total_found} relevant memories:")
            for m in results.memories:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.info(f"**{m.category.upper()}** — {m.content}")
                with col2:
                    st.metric("Relevance", f"{m.relevance:.2f}")
        else:
            st.warning("No relevant memories found.")