from adaptive_agent_memory import AdaptiveMemory, Experience


def test_record_recall_and_stats(tmp_path):
    db = tmp_path / "memory.db"
    memory = AdaptiveMemory(db)
    memory.record(
        Experience(
            context="Need weather for Berlin",
            action="weather_tool",
            expected_outcome="temperature",
            actual_outcome="21 C and rain",
            success=1.0,
            tags=["weather", "tool"],
        )
    )

    matches = memory.recall("weather Hamburg")
    assert matches
    assert matches[0].experience.action == "weather_tool"

    stats = memory.stats()
    assert stats["count"] == 1
    assert stats["average_success"] == 1.0


def test_validation_rejects_invalid_success(tmp_path):
    memory = AdaptiveMemory(tmp_path / "memory.db")
    exp = Experience(
        context="x",
        action="tool",
        expected_outcome="ok",
        actual_outcome="ok",
        success=1.5,
    )

    try:
        memory.record(exp)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
