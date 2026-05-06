from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class Memory:
    """
    A single memory entry stored by the agent.

    Attributes:
        id          : unique memory identifier
        content     : the fact or information extracted from conversation
        category    : type of memory (fact, preference, decision, context)
        created_at  : timestamp when memory was created
        relevance   : relevance score when retrieved (0.0 - 1.0)
    """
    id: str
    content: str
    category: str = "fact"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    relevance: float = 0.0

    def __str__(self) -> str:
        return f"[{self.category.upper()}] {self.content}"


@dataclass
class MemorySearchResult:
    """
    Result returned when searching agent memories.

    Attributes:
        memories    : list of relevant Memory objects
        query       : the search query used
        total_found : total number of memories found
    """
    memories: List[Memory] = field(default_factory=list)
    query: str = ""
    total_found: int = 0

    def __str__(self) -> str:
        if not self.memories:
            return "No relevant memories found."
        lines = [f"Found {self.total_found} relevant memories:"]
        for m in self.memories:
            lines.append(f"  • {m}")
        return "\n".join(lines)