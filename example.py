from agentmemory import AgentMemory

# Initialise memory store
memory = AgentMemory(memory_path="agent_memory.json")

print("=== AgentMemory Demo ===\n")

# Store some memories
print("Storing memories...")
stored = memory.remember(
    "I am building a RAG application using Python and OpenAI. "
    "I prefer concise answers and clean code. "
    "I am working on a hallucination detection library called HallucinationBench."
)

for m in stored:
    print(f"  Stored: {m}")

print(f"\nTotal memories: {memory.count}\n")

# Recall relevant memories
print("Recalling memories about RAG...")
results = memory.recall("What is the user building?")
print(results)

print("\nRecalling memories about preferences...")
results = memory.recall("What does the user prefer?")
print(results)