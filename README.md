# Adaptive Agent Memory

AI agents need more than a rolling chat history — they need structured, searchable, scoreable, and persistent memory.

Adaptive Agent Memory provides a robust, lightweight memory system for AI agents, allowing them to recall relevant information efficiently based on relevance, quality, and recency, solving the problem of context window limits and irrelevant context retrieval.

[![PyPI version](https://img.shields.io/pypi/v/adaptive-agent-memory)](https://pypi.org/project/adaptive-agent-memory/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/adaptive-agent-memory/adaptive-agent-memory-community/actions/workflows/ci.yml/badge.svg)](https://github.com/adaptive-agent-memory/adaptive-agent-memory-community/actions/workflows/ci.yml)

## Installation

```bash
pip install adaptive-agent-memory
```

## Why not just use chat history?

Dumping the entire chat history into your LLM prompt scales terribly. It wastes tokens, dilutes context, and lacks structure. 

Adaptive Agent Memory provides:
*   **Structured:** Data is stored with metadata, not just raw text.
*   **Searchable:** Find exact or semantically similar memories.
*   **Scoreable:** Memories are ranked dynamically.
*   **Persistent:** Long-term storage beyond a single session.

## Quickstart

```python
from adaptive_memory import MemorySystem

memory = MemorySystem()
memory.add("User's favorite color is blue", tags=["user_pref"])

# Later, when the agent needs context:
relevant_memories = memory.retrieve(query="What does the user like?", top_k=1)
print(relevant_memories[0].content) # Output: User's favorite color is blue
```

## How it works

Retrieval isn't just about semantic similarity. We use a composite scoring formula to surface the most useful memories:

`Score = (Relevance * W_rel) + (Quality * W_qual) + (Recency * W_rec)`

*   **Relevance:** How well the memory matches the query (e.g., embeddings, BM25).
*   **Quality:** How useful the memory has proven to be in the past (reinforcement).
*   **Recency:** How new the memory is (with configurable decay).

## Community vs Pro

| Feature | Community | Pro |
| :--- | :--- | :--- |
| Core Memory Storage | ✅ | ✅ |
| Basic Retrieval | ✅ | ✅ |
| Local Persistence (JSON/SQLite) | ✅ | ✅ |
| Advanced Embeddings & Vector DBs | ❌ | ✅ |
| Multi-Agent Shared Memory | ❌ | ✅ |
| Dynamic Memory Consolidation | ❌ | ✅ |
| Cloud Sync & Enterprise Auth | ❌ | ✅ |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
