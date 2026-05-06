# 🧠 AgentMemory

**Persistent memory for your OpenAI agents — store, recall, and forget.**

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![OpenAI](https://img.shields.io/badge/powered%20by-OpenAI-412991)

---

## The problem

Every OpenAI agent starts from zero. No memory of past conversations,
preferences, decisions, or context. Every session is a blank slate.

**AgentMemory solves this — giving your agent durable, queryable memory
that persists across sessions.**

---

## Quickstart

Install dependencies:

```bash
pip install openai python-dotenv
```

Set your OpenAI API key:

```bash
# .env
OPENAI_API_KEY=your_key_here
```

Run your first memory session:

```python
from agentmemory import AgentMemory

memory = AgentMemory(memory_path="agent_memory.json")

# Store memories from any text
memory.remember(
    "I am building a RAG application using Python and OpenAI. "
    "I prefer concise answers and clean code."
)

# Recall relevant memories
results = memory.recall("What is the user building?")
print(results)
```

Output:

```
Found 2 relevant memories:
  • [CONTEXT] User is building a RAG application using Python and OpenAI
  • [CONTEXT] User prefers concise answers and clean code
```

---

## API Reference

```python
memory = AgentMemory(
    memory_path="agent_memory.json",  # local storage file
    model="gpt-4o-mini",              # judge model
    max_memories=100,                 # max memories to store
)

memory.remember(text)        # extract and store memories from text
memory.recall(query, top_k)  # retrieve relevant memories
memory.forget(memory_id)     # delete a specific memory
memory.forget_all()          # clear all memories
memory.list_all()            # return all stored memories
memory.count                 # total number of memories
```

---

## Memory categories

| Category | Description |
|----------|-------------|
| `fact` | Factual statements about the user or domain |
| `preference` | User preferences and style choices |
| `decision` | Decisions made during conversations |
| `context` | Project or situational context |

---

## Streamlit demo

Run the interactive demo locally:

```bash
streamlit run app.py
```

Features:

- Store memories from any text input
- Search memories with semantic recall
- View all stored memories in the sidebar
- Delete individual memories or clear all

---

## How it works

1. `remember(text)` sends the text to GPT-4o-mini which extracts
   individual factual claims, preferences, decisions, and context.
2. Each memory is stored as a structured object in a local JSON file.
3. `recall(query)` sends the query and all stored memories to
   GPT-4o-mini which scores each memory for relevance.
4. Memories are returned ranked by relevance score.

All storage is **local** — no cloud, no database, no infrastructure.
Just a JSON file on your machine.

---

## Cost

Each `remember()` call: **~$0.001**

Each `recall()` call: **~$0.001**

Both use GPT-4o-mini as the judge.

---

## Roadmap

- [ ] Vector embedding search for faster recall at scale
- [ ] Memory expiry and TTL support
- [ ] Memory categories and filtering
- [ ] LangChain and LlamaIndex integration hooks
- [ ] Multi-agent shared memory support

---

## Project structure

```
agentmemory/
├── agentmemory/
│   ├── __init__.py       # public API
│   ├── memory.py         # AgentMemory core class
│   └── models.py         # Memory and MemorySearchResult dataclasses
├── app.py                # Streamlit demo
├── example.py            # quickstart example
├── requirements.txt
├── .env.example
└── README.md
```

---

## License

MIT — free to use, modify, and distribute.

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss
what you would like to change.

---

*Built with OpenAI GPT-4o-mini as the memory extraction and recall judge.*