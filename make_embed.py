#!/usr/bin/env python3
"""
make_embed.py — Sinh link nhúng web chart từ file JSON số liệu.

Cách dùng:
  python3 make_embed.py data/geekbench6.json https://username.github.io/tinhte-charts/chart.html

In ra Markdown chứa: link trực tiếp, mã iframe, gợi ý BBCode — dùng làm release notes.
"""
import base64
import json
import sys
from pathlib import Path


def main():
    cfg_path = sys.argv[1]
    base_url = sys.argv[2].rstrip("/").split("?")[0]

    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    raw = json.dumps(cfg, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    d = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    url = f"{base_url}?d={d}"
    height = 180 + len(cfg.get("items", [])) * 46
    iframe = (f'<iframe src="{url}" width="100%" height="{height}" '
              f'frameborder="0" loading="lazy" scrolling="no"></iframe>')

   data_url = f"https://raw.githubusercontent.com/pnghuy/tinhte-charts/main/{cfg_path}"
    print(f"## {cfg.get('title', Path(cfg_path).stem)}\n")
    print("**File video (Assets bên dưới):**")
    print("- `_alpha.mov` — Premiere / DaVinci: kéo lên track trên, nền tự trong suốt")
    print("- `_greenscreen.mp4` — CapCut: Chroma Key chấm màu xanh")
    print("- `_preview.mp4` — xem thử\n")
    print("**DATA_URL dán vào JSFiddle:**")
    print(f"```\n{data_url}\n```")


if __name__ == "__main__":
    main()
