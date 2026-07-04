#!/usr/bin/env python3
"""
render_chart.py — Render bar chart benchmark động thành video overlay cho video review.

Output:
  1. <name>_alpha.mov  : ProRes 4444, nền TRONG SUỐT -> kéo vào Premiere/FCP/DaVinci làm layer overlay
  2. <name>_preview.mp4: H.264 nền tối -> xem nhanh / dùng cho CapCut (chroma key nếu cần)

Cách dùng:
  python3 render_chart.py chart_config.json [ten_output]
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def render(cfg_path: str, out_name: str = "chart"):
    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))

    W, H = cfg.get("width", 1920), cfg.get("height", 1080)
    fps = cfg.get("fps", 30)
    duration = cfg.get("duration", 4.0)     # thời gian animation
    hold = cfg.get("hold", 1.5)             # giữ khung cuối
    stagger = cfg.get("stagger", 0.18)      # độ trễ giữa các thanh (giây)
    bar_anim = cfg.get("bar_anim", 1.2)     # thời gian 1 thanh chạy hết (giây)
    items = cfg["items"]
    n = len(items)
    max_val = max(it["value"] for it in items)

    total_frames = int((duration + hold) * fps)
    frames_dir = Path("frames")
    frames_dir.mkdir(exist_ok=True)
    for f in frames_dir.glob("*.png"):
        f.unlink()

    dpi = 100
    fig_w, fig_h = W / dpi, H / dpi

    for frame in range(total_frames):
        t = frame / fps

        fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
        fig.patch.set_alpha(0.0)  # nền trong suốt
        ax = fig.add_axes([0.28, 0.10, 0.62, 0.72])
        ax.patch.set_alpha(0.0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, max_val * 1.18)
        ax.set_ylim(-0.6, n - 0.4)
        ax.invert_yaxis()

        # Title + subtitle (fade in)
        title_alpha = ease_out_cubic(t / 0.5)
        fig.text(0.05, 0.90, cfg.get("title", ""), fontsize=34, fontweight="bold",
                 color="white", alpha=title_alpha)
        if cfg.get("subtitle"):
            fig.text(0.05, 0.855, cfg["subtitle"], fontsize=17,
                     color="#BBBBBB", alpha=title_alpha)

        for i, it in enumerate(items):
            start = 0.35 + i * stagger
            p = ease_out_cubic((t - start) / bar_anim)
            val_now = it["value"] * p
            hl = it.get("highlight", False)
            color = it["color"]
            bar_h = 0.62

            if p > 0:
                # bar nền mờ
                ax.barh(i, max_val * 1.05, height=bar_h, color="white", alpha=0.07 * p)
                ax.barh(i, val_now, height=bar_h, color=color,
                        alpha=1.0 if hl else 0.85, zorder=3)
                # số đếm chạy
                ax.text(val_now + max_val * 0.015, i, f"{val_now:,.0f}",
                        va="center", ha="left", fontsize=21,
                        fontweight="bold" if hl else "normal",
                        color="white", zorder=4)
            # tên thiết bị
            name_alpha = ease_out_cubic((t - start) / 0.4)
            if name_alpha > 0:
                ax.text(-max_val * 0.02, i, it["name"], va="center", ha="right",
                        fontsize=19, fontweight="bold" if hl else "normal",
                        color="white", alpha=name_alpha)

        # đơn vị
        if cfg.get("unit"):
            fig.text(0.90, 0.055, cfg["unit"], fontsize=14, color="#888888",
                     ha="right", alpha=title_alpha)

        fig.savefig(frames_dir / f"f{frame:05d}.png", transparent=True)
        plt.close(fig)

    # 1) ProRes 4444 alpha — cho Premiere / Final Cut / DaVinci
    mov = f"{out_name}_alpha.mov"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", str(frames_dir / "f%05d.png"),
        "-c:v", "prores_ks", "-profile:v", "4444",
        "-pix_fmt", "yuva444p10le", mov
    ], check=True, capture_output=True)

    # 2) MP4 preview nền tối
    mp4 = f"{out_name}_preview.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", str(frames_dir / "f%05d.png"),
        "-filter_complex",
        f"color=c=0x111318:s={W}x{H}:r={fps}[bg];[bg][0:v]overlay=shortest=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", mp4
    ], check=True, capture_output=True)

    # 3) MP4 nền xanh lá — cho CapCut (Chroma Key)
    green = f"{out_name}_greenscreen.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", str(frames_dir / "f%05d.png"),
        "-filter_complex",
        f"color=c=0x00FF00:s={W}x{H}:r={fps}[bg];[bg][0:v]overlay=shortest=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", green
    ], check=True, capture_output=True)

    print(f"Done: {mov}, {mp4}, {green}")


if __name__ == "__main__":
    cfg = sys.argv[1] if len(sys.argv) > 1 else "chart_config.json"
    name = sys.argv[2] if len(sys.argv) > 2 else "chart"
    render(cfg, name)
