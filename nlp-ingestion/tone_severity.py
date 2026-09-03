def refine_risk_with_tone(base_risk: str, tone: float) -> str:
    """Bumps a keyword-based risk level up one tier if coverage tone is very negative."""
    levels = ["low", "medium", "high"]
    idx = levels.index(base_risk) if base_risk in levels else 0
    if tone <= -5.0:
        idx = min(idx + 1, len(levels) - 1)   # very negative tone: bump severity up
    elif tone >= 3.0:
        idx = max(idx - 1, 0)                  # surprisingly positive tone: ease off
    return levels[idx]
