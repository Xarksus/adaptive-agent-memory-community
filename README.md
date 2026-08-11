# Adaptive Agent Memory Community

Adaptive Agent Memory Community is the open-source core of Adaptive Agent Memory.

It gives Python AI agents a lightweight local **experience memory**: store what happened, score outcomes, recall similar prior experiences, and inspect simple statistics before choosing a new action.

## Community features

- dependency-free Python core
- SQLite persistence
- experience recording
- success and prediction-error tracking
- relevance + recency retrieval
- advisory summaries
- basic statistics
- JSON export

## Quick start

```bash
pip install -e .
```

```python
from adaptive_agent_memory import AdaptiveMemory, Experience

memory = AdaptiveMemory("agent_memory.db")
memory.record(
    Experience(
        context="Need weather for Berlin",
        action="weather_tool",
        expected_outcome="current weather",
        actual_outcome="21 C and rain",
        success=1.0,
        tags=["weather", "tool"],
    )
)

print(memory.recall("weather Hamburg"))
print(memory.stats())
```

## Pro edition

The paid Pro layer adds **experience-to-decision learning** rather than only memory storage:

- action recommendations from prior outcomes
- adaptive weighting from success/failure and prediction error
- candidate-action filtering
- confidence estimates
- global action-performance analytics
- future advanced ranking and migration tooling

Current target pricing: EUR 49 Indie / EUR 99 Commercial.

## License

Community edition: MIT License.

The Pro package is separate proprietary software and is not part of this repository.
