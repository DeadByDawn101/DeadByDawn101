#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

AUTHOR = "deadbydawn101"
API_URL = f"https://huggingface.co/api/models?author={AUTHOR}&limit=100&full=true"
README = Path(__file__).resolve().parents[1] / "README.md"

with urllib.request.urlopen(API_URL, timeout=30) as r:
    models = json.load(r)

models = sorted(models, key=lambda m: (m.get("downloads") or 0), reverse=True)
model_count = len(models)
total_downloads = sum((m.get("downloads") or 0) for m in models)
total_likes = sum((m.get("likes") or 0) for m in models)

def badge(label, message, color="c084fc", label_color="0a000f"):
    from urllib.parse import quote
    safe_message = str(message).replace('-', '--').replace('_', '__')
    return f"https://img.shields.io/badge/{quote(label)}-{quote(safe_message)}-{color}?style=for-the-badge&labelColor={label_color}"

rows = []
emoji_cycle = ["🔥", "⚡", "💀", "🌀", "🔧", "🖤"]
for i, m in enumerate(models):
    mid = m["id"]
    short = mid.split("/", 1)[1]
    size = m.get("safetensors", {}).get("total") or m.get("usedStorage") or 0
    size_gb = f"{size / (1024**3):.2f} GB" if size else "—"
    downloads = f"**{(m.get('downloads') or 0):,}**"
    rows.append(f"| {emoji_cycle[i % len(emoji_cycle)]} | [**{short}**](https://huggingface.co/{mid}) | {size_gb} | {downloads} |")

table = "\n".join([
    "| | Model | Size | Downloads |",
    "|---|---|---|---|",
    *rows,
])

readme = README.read_text()

import re
readme = re.sub(
    r'<img src="https://img\.shields\.io/badge/HuggingFace-[^"]+"/>',
    f'<img src="{badge("HuggingFace", f"{model_count} Models")}"/>',
    readme,
    count=1,
)

top_model_downloads = f"#{models[0].get('downloads', 0):,}"

stats_block = "\n".join([
    '<!-- HF_STATS:START -->',
    f'<img src="{badge("HF Downloads", f"{total_downloads:,}")}"/>',
    '&nbsp;&nbsp;',
    f'<img src="{badge("HF Likes", f"{total_likes}")}"/>',
    '&nbsp;&nbsp;',
    f'<img src="{badge("Top Model", top_model_downloads, color="6a0dad")}"/>',
    '<!-- HF_STATS:END -->',
])

if '<!-- HF_STATS:START -->' in readme:
    readme = re.sub(r'<!-- HF_STATS:START -->.*?<!-- HF_STATS:END -->', stats_block, readme, flags=re.S)
else:
    readme = readme.replace('</div>\n\n<br/>', f'</div>\n\n<div align="center">\n\n{stats_block}\n\n</div>\n\n<br/>', 1)

new_section = f"""## 🤗 &nbsp;HuggingFace — MLX Models\n\n> *All models: native tool calling · Apple Silicon · Ollama-ready*\n\n{table}\n"""
readme = re.sub(r'## 🤗 &nbsp;HuggingFace — MLX Models.*?\n\n\*\*Live Demos:\*\*', new_section + "\n**Live Demos:**", readme, flags=re.S)

README.write_text(readme)
print(f"Updated README with {model_count} models, {total_downloads} downloads, {total_likes} likes")
