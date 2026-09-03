from filter_disruption_events import pull_with_themes
from tone_severity import refine_risk_with_tone
from extract_entities import extract

articles = pull_with_themes('supply chain disruption', 5)
for a in articles:
    event = extract(a)
    base = 'low'
    if event['event_type'] in ['LABOR_STRIKE', 'NATURAL_DISASTER']: base = 'high'
    elif event['event_type'] in ['TRADE_ACTION', 'LOGISTICS_DELAY']: base = 'medium'
    tone = float(a.get('tone', 0) or 0)
    print(f"Title: {a.get('title')}\nTone: {tone}\nBase Risk: {base} -> Refined Risk: {refine_risk_with_tone(base, tone)}\n")
