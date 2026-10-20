"""Rule-based NLP entity extraction baseline for incident reports."""
import re
KEYWORDS = {
 "emergency_type": {
  "injury":["injured","fell","fall","bleeding","ankle","pain","wound"],
  "lost_hiker":["lost","missing","cannot identify","wrong path","separated"],
  "landslide":["landslide","slope is moving","debris","rocks blocked"],
  "flooding":["flood","rising water","fast-flowing stream","river crossing"],
  "dehydration_fatigue":["dizzy","dehydrated","exhausted","fatigue","faint","cramps"],
  "wildlife_encounter":["wild animal","wildlife","animal encounter"],
  "severe_weather":["thunderstorm","strong winds","heavy rain","poor visibility","mist"],
  "trail_blockage":["fallen tree","blocked trail","damaged bridge","obstacle"]
 },
 "severity_indicators": {
  "high":["cannot walk","unconscious","severe bleeding","trapped","immediate assistance"],
  "moderate":["pain","dizzy","poor visibility","heavy rain","lost"],
  "low":["minor","small cut","safe"]
 },
 "context": {
  "heavy_rain":["heavy rain","heavy rainfall","flood"],
  "poor_visibility":["poor visibility","mist","fog"],
  "remote_area":["remote","far from trailhead","no signal"],
  "low_battery":["battery is low","low battery","phone battery"]
 }
}
def extract(text):
    t = text.lower()
    out = {}
    for group, labels in KEYWORDS.items():
        found = []
        for label, words in labels.items():
            if any(w in t for w in words):
                found.append(label)
        out[group] = found
    return out
if __name__ == "__main__":
    sample = "We are lost in heavy rain, poor visibility, and phone battery is low."
    print(extract(sample))
