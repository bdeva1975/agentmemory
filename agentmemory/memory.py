import os
import json
import uuid
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from agentmemory.models import Memory, MemorySearchResult

load_dotenv()

_client = None


def _get_client() -> OpenAI:
    """Lazy-initialise the OpenAI client once."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY not found. "
                "Set it in your .env file or as an environment variable."
            )
        http_client = httpx.Client(verify=False)
        _client = OpenAI(api_key=api_key, http_client=http_client)
    return _client


_EXTRACT_PROMPT = """
You are a memory extraction assistant.

Given a conversation message, extract all factual claims, preferences, 
decisions, or important context that an AI agent should remember for 
future conversations.

Return ONLY a valid JSON object with a single key "memories" containing an array.
No explanation. No markdown. Raw JSON only.

Each item must follow this schema:
{
  "content": "the memory to store as a short clear sentence",
  "category": "fact | preference | decision | context"
}

Example output:
{"memories": [
  {"content": "User prefers Python over JavaScript", "category": "preference"},
  {"content": "User is building a RAG application", "category": "context"}
]}

If nothing meaningful to extract, return {"memories": []}
""".strip()

_SEARCH_PROMPT = """
You are a memory relevance judge.

Given a query and a list of memories, return the indices of memories 
that are relevant to the query, along with a relevance score.

Return ONLY a valid JSON object with a single key "results" containing an array.
No explanation. No markdown. Raw JSON only.

Each item must follow this schema:
{
  "index": 0,
  "relevance": 0.95
}

Return {"results": []} if no memories are relevant.
Relevance score must be between 0.0 and 1.0.
Only include memories with relevance >= 0.5.
""".strip()


class AgentMemory:
    """
    Persistent memory store for OpenAI agents.

    Stores memories in a local JSON file and retrieves
    relevant memories using GPT-4o-mini as a semantic judge.

    Usage:
        memory = AgentMemory(memory_path="agent_memory.json")
        memory.remember("User told me they prefer concise answers.")
        results = memory.recall("What does the user prefer?")
        print(results)
    """

    def __init__(
        self,
        memory_path: str = "agent_memory.json",
        model: str = "gpt-4o-mini",
        max_memories: int = 100,
    ):
        self.memory_path = memory_path
        self.model = model
        self.max_memories = max_memories
        self._memories: List[Memory] = []
        self._load()

    def _load(self):
        """Load memories from the JSON file."""
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._memories = [Memory(**m) for m in data]
            except Exception:
                self._memories = []

    def _save(self):
        """Save memories to the JSON file."""
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(
                [m.__dict__ for m in self._memories],
                f,
                indent=2,
                ensure_ascii=False,
            )

    def remember(self, text: str) -> List[Memory]:
        """
        Extract and store memories from a text input.

        Args:
            text: conversation message or any text to extract memories from

        Returns:
            List of Memory objects that were stored
        """
        if not text or not text.strip():
            return []

        client = _get_client()

        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _EXTRACT_PROMPT},
                    {"role": "user", "content": text.strip()},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            raw = completion.choices[0].message.content
        except Exception as e:
            return []

        try:
            parsed = json.loads(raw)
            items = parsed.get("memories", [])
        except json.JSONDecodeError:
            return []

        new_memories = []
        for item in items:
            if isinstance(item, dict) and "content" in item:
                memory = Memory(
                    id=str(uuid.uuid4()),
                    content=item["content"],
                    category=item.get("category", "fact"),
                )
                self._memories.append(memory)
                new_memories.append(memory)

        if len(self._memories) > self.max_memories:
            self._memories = self._memories[-self.max_memories:]

        self._save()
        return new_memories

    def recall(
        self,
        query: str,
        top_k: int = 5,
    ) -> MemorySearchResult:
        """
        Retrieve memories relevant to a query.

        Args:
            query: the question or context to search memories for
            top_k: maximum number of memories to return

        Returns:
            MemorySearchResult with relevant memories and scores
        """
        if not self._memories:
            return MemorySearchResult(query=query)

        if not query or not query.strip():
            return MemorySearchResult(query=query)

        client = _get_client()

        memories_list = "\n".join(
            f"{i}: {m.content} [{m.category}]"
            for i, m in enumerate(self._memories)
        )

        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SEARCH_PROMPT},
                    {
                        "role": "user",
                        "content": f"QUERY: {query.strip()}\n\nMEMORIES:\n{memories_list}",
                    },
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            raw = completion.choices[0].message.content
        except Exception as e:
            return MemorySearchResult(query=query)

        try:
            parsed = json.loads(raw)
            items = parsed.get("results", [])
        except json.JSONDecodeError:
            return MemorySearchResult(query=query)

        relevant = []
        for item in items:
            if isinstance(item, dict) and "index" in item:
                idx = item["index"]
                if 0 <= idx < len(self._memories):
                    memory = self._memories[idx]
                    memory.relevance = float(item.get("relevance", 0.5))
                    relevant.append(memory)

        relevant.sort(key=lambda m: m.relevance, reverse=True)
        relevant = relevant[:top_k]

        return MemorySearchResult(
            memories=relevant,
            query=query,
            total_found=len(relevant),
        )

    def forget(self, memory_id: str) -> bool:
        """
        Delete a specific memory by ID.

        Args:
            memory_id: the ID of the memory to delete

        Returns:
            True if deleted, False if not found
        """
        original_count = len(self._memories)
        self._memories = [m for m in self._memories if m.id != memory_id]
        if len(self._memories) < original_count:
            self._save()
            return True
        return False

    def forget_all(self):
        """Clear all memories."""
        self._memories = []
        self._save()

    def list_all(self) -> List[Memory]:
        """Return all stored memories."""
        return self._memories.copy()

    @property
    def count(self) -> int:
        """Total number of stored memories."""
        return len(self._memories)