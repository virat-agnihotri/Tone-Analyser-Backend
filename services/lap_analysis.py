def analyze_lap_data(laps: list, stress_score: float) -> dict:
    if not laps:
        return {
            "laps": [],
            "average_lap_time": None,
            "observations": [
                "No telemetry lap data attached to this session. Voice metrics analyzed independently."
            ]
        }

    observations = []
    lap_times = [
        lap.get("lap_time") for lap in laps
        if isinstance(lap, dict) and lap.get("lap_time") is not None
    ]

    if lap_times:
        average_time = sum(lap_times) / len(lap_times)
        for lap in laps:
            lap_time = lap.get("lap_time")
            if lap_time and lap_time > average_time * 1.03:
                observations.append(
                    f"Lap {lap.get('lap_number', '?')} was significantly slower than session average."
                )

    if stress_score >= 70:
        observations.append(
            "High driver stress detected. Check cornering consistency during high-wear laps."
        )

    return {
        "laps": laps,
        "average_lap_time": round(sum(lap_times) / len(lap_times), 3) if lap_times else None,
        "observations": observations
    }