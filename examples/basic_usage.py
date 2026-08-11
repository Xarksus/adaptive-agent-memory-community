from adaptive_agent_memory import AdaptiveMemory, Experience

memory = AdaptiveMemory("demo_memory.db")

memory.record(
    Experience(
        context="User asks for the current weather in Berlin",
        action="weather_tool",
        expected_outcome="A current weather report",
        actual_outcome="Returned temperature, rain probability, and wind",
        success=1.0,
        prediction_error=0.0,
        tags=["weather", "tool-use"],
    )
)

print(memory.advise("Get the weather for Hamburg"))
print(memory.stats())
