#!/usr/bin/env python3
"""
render_chart.py v2 — Render bar chart benchmark động thành video overlay.

Hỗ trợ 2 kiểu JSON:
  1. Đơn:  items có "value" (+ "color")          -> mỗi máy một thanh
  2. Nhóm: có "series": [...] và "seriesColors",
           items có "values": [v1, v2, ...]       -> mỗi máy 2-3 thanh

Output:
  <name>_alpha.mov       ProRes 4444 nền trong suốt (Premiere/FCP/DaVinci)
  <name>_preview.mp4     nền tối để xem thử
  <name>_greenscreen.mp4 nền xanh cho CapCut (Chroma Key)

Cách dùng: python3 render_chart.py data/xxx.json ten_output
"""

import json
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DEFAULT_SERIES_COLORS = ["#0088CC", "#6CBE45", "#F5A623"]


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def render(cfg_path: str, out_name: str = "chart"):
    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))

    W, H = cfg.get("width", 1920), cfg.get("height", 1080)
    fps = cfg.get("fps", 30)
    duration = cfg.get("duration", 4.0)
    hold = cfg.get("hold", 1.5)
    stagger = cfg.get("stagger", 0.18)
    bar_anim = cfg.get("bar_anim", 1.2)
    items = cfg["items"]
    n = len(items)

    series = cfg.get("series")
    grouped = bool(series)
    s_colors = cfg.get("seriesColors", DEFAULT_SERIES_COLORS)
    n_series = len(series) if grouped else 1

    if grouped:
        max_val = max(v for it in items for v in it["values"])
    else:
        max_val = max(it["value"] for it in items)

    total_frames = int((duration + hold) * fps)
    frames_dir = Path("frames")
    frames_dir.mkdir(exist_ok=True)
    for f in frames_dir.glob("*.png"):
        f.unlink()

    dpi = 100
    fig_w, fig_h = W / dpi, H / dpi

    # Kích thước cụm thanh
    group_h = 0.68                      # tổng bề dày cụm của 1 máy
    gap = 0.06                          # khe giữa các thanh con
    sub_h = (group_h - gap * (n_series - 1)) / n_series

    for frame in range(total_frames):
        t = frame / fps

        fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
        fig.patch.set_alpha(0.0)
        ax = fig.add_axes([0.28, 0.10, 0.62, 0.70 if grouped else 0.72])
        ax.patch.set_alpha(0.0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, max_val * 1.18)
        ax.set_ylim(-0.6, n - 0.4)
        ax.invert_yaxis()

        title_alpha = ease_out_cubic(t / 0.5)
        fig.text(0.05, 0.90, cfg.get("title", ""), fontsize=34, fontweight="bold",
                 color="white", alpha=title_alpha)
        if cfg.get("subtitle"):
            fig.text(0.05, 0.855, cfg["subtitle"], fontsize=17,
                     color="#BBBBBB", alpha=title_alpha)

        # Chú giải series
        if grouped:
            lx = 0.28
            for si, sname in enumerate(series):
                c = s_colors[si % len(s_colors)]
                fig.patches.append(plt.Rectangle(
                    (lx, 0.815), 0.012, 0.018, transform=fig.transFigure,
                    facecolor=c, alpha=title_alpha, edgecolor="none"))
                fig.text(lx + 0.018, 0.816, sname, fontsize=14,
                         color="white", alpha=title_alpha, va="bottom")
                lx += 0.018 + 0.012 * len(sname) + 0.03

        for i, it in enumerate(items):
            hl = it.get("highlight", False)
            start = 0.35 + i * stagger

            vals = it["values"] if grouped else [it["value"]]
            for si, v in enumerate(vals):
                p = ease_out_cubic((t - start - si * 0.08) / bar_anim)
                if grouped:
                    color = s_colors[si % len(s_colors)]
                else:
                    color = it.get("color", "#E53935" if hl else "#9E9E9E")
                # tâm thanh con si trong cụm của máy i
                y = i - group_h / 2 + sub_h / 2 + si * (sub_h + gap)
                val_now = v * p
                if p > 0:
                    ax.barh(y, max_val * 1.05, height=sub_h, color="white",
                            alpha=0.07 * p)
                    ax.barh(y, val_now, height=sub_h, color=color,
                            alpha=1.0 if (hl or grouped) else 0.85, zorder=3)
                    ax.text(val_now + max_val * 0.015, y, f"{val_now:,.0f}",
                            va="center", ha="left",
                            fontsize=15 if grouped else 21,
                            fontweight="bold" if hl else "normal",
                            color="white", zorder=4)

            name_alpha = ease_out_cubic((t - start) / 0.4)
            if name_alpha > 0:
                ax.text(-max_val * 0.02, i, it["name"], va="center", ha="right",
                        fontsize=19, fontweight="bold" if hl else "normal",
                        color="white", alpha=name_alpha)

        if cfg.get("unit"):
            fig.text(0.90, 0.055, cfg["unit"], fontsize=14, color="#888888",
                     ha="right", alpha=title_alpha)

        fig.savefig(frames_dir / f"f{frame:05d}.png", transparent=True)
        plt.close(fig)

    mov = f"{out_name}_alpha.mov"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", str(frames_dir / "f%05d.png"),
        "-c:v", "prores_ks", "-profile:v", "4444",
        "-pix_fmt", "yuva444p10le", mov
    ], check=True, capture_output=True)

    mp4 = f"{out_name}_preview.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", str(frames_dir / "f%05d.png"),
        "-filter_complex",
        f"color=c=0x111318:s={W}x{H}:r={fps}[bg];[bg][0:v]overlay=shortest=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", mp4
    ], check=True, capture_output=True)

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
