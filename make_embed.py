#!/usr/bin/env python3
"""
make_embed.py — Sinh release notes: link video + DATA_URL cho JSFiddle.

Cách dùng:
  python3 make_embed.py data/2026-07-zephyrus-duo/pcmark10.json <base_url>
(base_url không còn dùng nhưng giữ tham số để khỏi sửa workflow)
"""
import json
import sys
from pathlib import Path


def main():
    cfg_path = sys.argv[1]
    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    data_url = f"https://raw.githubusercontent.com/pnghuy/tinhte-charts/main/{cfg_path}"

    print(f"## {cfg.get('title', Path(cfg_path).stem)}\n")
    print("**File video (Assets bên dưới):**")
    print("- `_alpha.mov` — Premiere / Final Cut / DaVinci: kéo lên track trên, nền tự trong suốt")
    print("- `_greenscreen.mp4` — CapCut: Chroma Key chấm màu xanh")
    print("- `_preview.mp4` — xem thử\n")
    print("**DATA_URL dán vào JSFiddle:**")
    print(f"```\n{data_url}\n```")


if __name__ == "__main__":
    main()
