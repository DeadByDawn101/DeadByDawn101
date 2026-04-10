#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path
import urllib.request

MODEL_ID = "deadbydawn101/gemma-4-E4B-opus-reasoning-claude-code-lora"
API_URL = f"https://huggingface.co/api/models/{MODEL_ID}"
ROOT = Path(__file__).resolve().parents[1]
HISTORY_DIR = ROOT / "data"
HISTORY_DIR.mkdir(exist_ok=True)
HISTORY_FILE = HISTORY_DIR / "hf_model_history.json"
README = ROOT / "README.md"

with urllib.request.urlopen(API_URL, timeout=30) as r:
    model = json.load(r)

entry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "model": MODEL_ID,
    "downloads": model.get("downloads", 0),
    "likes": model.get("likes", 0),
}

history = []
if HISTORY_FILE.exists():
    history = json.loads(HISTORY_FILE.read_text())

if not history or history[-1].get("downloads") != entry["downloads"] or history[-1].get("likes") != entry["likes"]:
    history.append(entry)
    HISTORY_FILE.write_text(json.dumps(history, indent=2) + "\n")

current = history[-1]
previous = history[-2] if len(history) > 1 else None

delta_downloads = current["downloads"] - previous["downloads"] if previous else 0
delta_likes = current["likes"] - previous["likes"] if previous else 0

milestones = [1, 5, 10, 25, 50, 100, 250, 500, 1000]
next_milestone = next((m for m in milestones if current["downloads"] < m), None)
remaining = (next_milestone - current["downloads"]) if next_milestone is not None else 0

snippet = "\n".join([
    "<!-- HF_LORA_TRACKER:START -->",
    '<img src="https://img.shields.io/badge/LoRA%20Downloads-' + f'{current["downloads"]:,}'.replace(',', '%2C') + '-c084fc?style=for-the-badge&labelColor=0a000f"/>',
    '&nbsp;&nbsp;',
    '<img src="https://img.shields.io/badge/LoRA%20Delta-' + (f'{delta_downloads:+}'.replace('+', '%2B')) + '-6a0dad?style=for-the-badge&labelColor=0a000f"/>',
    '&nbsp;&nbsp;',
    '<img src="https://img.shields.io/badge/Next%20Milestone-' + (f'{next_milestone} ({remaining} left)' if next_milestone is not None else 'tracking').replace(' ', '%20').replace('(', '%28').replace(')', '%29') + '-111111?style=for-the-badge&labelColor=0a000f"/>',
    '',
    f"- **Tracked model:** `{MODEL_ID}`",
    f"- **Current downloads:** **{current['downloads']:,}**",
    f"- **Current likes:** **{current['likes']}**",
    f"- **Delta since last change:** `{delta_downloads:+}` downloads, `{delta_likes:+}` likes",
    f"- **Last checked:** `{current['timestamp']}`",
    "<!-- HF_LORA_TRACKER:END -->",
])

readme = README.read_text()
if "<!-- HF_LORA_TRACKER:START -->" in readme:
    import re
    readme = re.sub(r'<!-- HF_LORA_TRACKER:START -->.*?<!-- HF_LORA_TRACKER:END -->', snippet, readme, flags=re.S)
else:
    anchor = "**Live Demos:**"
    readme = readme.replace(anchor, snippet + "\n\n" + anchor, 1)
README.write_text(readme)

print(f"Tracked {MODEL_ID}: downloads={current['downloads']} likes={current['likes']} delta={delta_downloads:+}")
