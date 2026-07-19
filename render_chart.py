#!/usr/bin/env python3
"""
render_chart.py v3 — Render bar chart benchmark động thành video overlay.

Mỗi file JSON ra 2 bản:
  NGANG 16:9 (mặc định 1920x1080) — cho video review chính:
    <name>_alpha.mov        ProRes 4444 nền trong suốt (Premiere/FCP/DaVinci)
    <name>_preview.mp4      nền tối xem thử
    <name>_greenscreen.mp4  nền xanh cho CapCut
  DỌC 9:16 (1080x1920) — cho Reels/TikTok/Shorts, layout riêng:
    <name>_doc_alpha.mov
    <name>_doc_greenscreen.mp4
  Tắt bản dọc cho một chart: thêm "portrait": false vào JSON.

Hỗ trợ 2 kiểu số liệu:
  Đơn:  items có "value" (+ "color")
  Nhóm: "series": [...], "seriesColors": [...], items có "values": [...]

Cách dùng: python3 render_chart.py data/xxx.json ten_output
"""

import json
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT_SERIES_COLORS = ["#0088CC", "#6CBE45", "#F5A623"]


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def load_cfg(cfg_path):
    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    series = cfg.get("series")
    grouped = bool(series)
    if grouped:
        max_val = max(v for it in cfg["items"] for v in it["values"])
    else:
        max_val = max(it["value"] for it in cfg["items"])
    return cfg, grouped, series or [], cfg.get("seriesColors", DEFAULT_SERIES_COLORS), max_val


def encode(frames_dir, fps, W, H, out_name, alpha=True, preview=False, green=True):
    outs = []
    if alpha:
        mov = f"{out_name}_alpha.mov"
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", str(frames_dir / "f%05d.png"),
            "-c:v", "prores_ks", "-profile:v", "4444",
            "-pix_fmt", "yuva444p10le", mov
        ], check=True, capture_output=True)
        outs.append(mov)
    if preview:
        mp4 = f"{out_name}_preview.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", str(frames_dir / "f%05d.png"),
            "-filter_complex",
            f"color=c=0x111318:s={W}x{H}:r={fps}[bg];[bg][0:v]overlay=shortest=1",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", mp4
        ], check=True, capture_output=True)
        outs.append(mp4)
    if green:
        g = f"{out_name}_greenscreen.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", str(frames_dir / "f%05d.png"),
            "-filter_complex",
            f"color=c=0x00FF00:s={W}x{H}:r={fps}[bg];[bg][0:v]overlay=shortest=1",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", g
        ], check=True, capture_output=True)
        outs.append(g)
    return outs


def clean_frames():
    frames_dir = Path("frames")
    frames_dir.mkdir(exist_ok=True)
    for f in frames_dir.glob("*.png"):
        f.unlink()
    return frames_dir


# ---------------- BẢN NGANG 16:9 ----------------
def render_landscape(cfg, grouped, series, s_colors, max_val, out_name):
    W, H = cfg.get("width", 1920), cfg.get("height", 1080)
    fps = cfg.get("fps", 30)
    duration, hold = cfg.get("duration", 4.0), cfg.get("hold", 1.5)
    stagger, bar_anim = cfg.get("stagger", 0.18), cfg.get("bar_anim", 1.2)
    items = cfg["items"]
    n = len(items)
    n_series = len(series) if grouped else 1

    total_frames = int((duration + hold) * fps)
    frames_dir = clean_frames()
    dpi = 100

    # Tu do ten dai nhat de tinh le trai -> ten dai khong bi lem, chart tu can
    name_fs = 19
    tmp = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi)
    renderer = tmp.canvas.get_renderer()
    max_name_px = 0
    for it in items:
        txt = tmp.text(0, 0, it["name"], fontsize=name_fs, fontweight="bold")
        max_name_px = max(max_name_px, txt.get_window_extent(renderer=renderer).width)
    plt.close(tmp)
    need_frac = (max_name_px + 50) / W
    left_frac = min(0.45, max(0.20, need_frac))
    if need_frac > 0.45:
        name_fs = max(13, int(name_fs * 0.45 / need_frac))

    group_h = 0.68
    gap = 0.06
    sub_h = (group_h - gap * (n_series - 1)) / n_series

    for frame in range(total_frames):
        t = frame / fps
        fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi)
        fig.patch.set_alpha(0.0)
        ax = fig.add_axes([left_frac, 0.10, 0.90 - left_frac, 0.70 if grouped else 0.72])
        ax.patch.set_alpha(0.0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlim(0, max_val * 1.18)
        ax.set_ylim(-0.6, n - 0.4)
        ax.invert_yaxis()

        title_alpha = ease_out_cubic(t / 0.5)
        fig.text(0.05, 0.90, cfg.get("title", ""), fontsize=34, fontweight="bold",
                 color="white", alpha=title_alpha)
        if cfg.get("subtitle"):
            fig.text(0.05, 0.855, cfg["subtitle"], fontsize=17,
                     color="#BBBBBB", alpha=title_alpha)

        if grouped:
            lx = left_frac
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
                color = (s_colors[si % len(s_colors)] if grouped
                         else it.get("color", "#E53935" if hl else "#9E9E9E"))
                y = i - group_h / 2 + sub_h / 2 + si * (sub_h + gap)
                val_now = v * p
                if p > 0:
                    ax.barh(y, max_val * 1.05, height=sub_h, color="white", alpha=0.07 * p)
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
                        fontsize=name_fs, fontweight="bold" if hl else "normal",
                        color="white", alpha=name_alpha)

        if cfg.get("unit"):
            fig.text(0.90, 0.055, cfg["unit"], fontsize=14, color="#888888",
                     ha="right", alpha=title_alpha)

        fig.savefig(frames_dir / f"f{frame:05d}.png", transparent=True)
        plt.close(fig)

    return encode(frames_dir, fps, W, H, out_name, alpha=True, preview=True, green=True)


# ---------------- BẢN DỌC 9:16 ----------------
def render_portrait(cfg, grouped, series, s_colors, max_val, out_name):
    W, H = cfg.get("portrait_width", 1080), cfg.get("portrait_height", 1920)
    fps = cfg.get("fps", 30)
    duration, hold = cfg.get("duration", 4.0), cfg.get("hold", 1.5)
    stagger, bar_anim = cfg.get("stagger", 0.18), cfg.get("bar_anim", 1.2)
    items = cfg["items"]
    n_series = len(series) if grouped else 1

    total_frames = int((duration + hold) * fps)
    frames_dir = clean_frames()
    dpi = 100

    # Layout dọc: tên máy nằm TRÊN thanh, thanh chạy full bề ngang,
    # số đếm cột phải — hợp khung đứng, không bị cụt tên.
    NAME_H, BAR_H, ITEM_GAP = 0.36, 0.34, 0.30
    block_h = NAME_H + n_series * BAR_H
    total_h = len(items) * (block_h + ITEM_GAP) - ITEM_GAP
    BAR_FRAC = 0.76  # thanh dài tối đa 76% bề ngang, chừa cột số bên phải

    for frame in range(total_frames):
        t = frame / fps
        fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi)
        fig.patch.set_alpha(0.0)
        ax = fig.add_axes([0.07, 0.06, 0.86, 0.76])
        ax.patch.set_alpha(0.0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, total_h)
        ax.invert_yaxis()

        title_alpha = ease_out_cubic(t / 0.5)
        fig.text(0.07, 0.945, cfg.get("title", ""), fontsize=40, fontweight="bold",
                 color="white", alpha=title_alpha)
        if cfg.get("subtitle"):
            fig.text(0.07, 0.918, cfg["subtitle"], fontsize=20,
                     color="#BBBBBB", alpha=title_alpha)

        if grouped:
            lx = 0.07
            for si, sname in enumerate(series):
                c = s_colors[si % len(s_colors)]
                fig.patches.append(plt.Rectangle(
                    (lx, 0.878), 0.020, 0.012, transform=fig.transFigure,
                    facecolor=c, alpha=title_alpha, edgecolor="none"))
                fig.text(lx + 0.028, 0.877, sname, fontsize=17,
                         color="white", alpha=title_alpha, va="bottom")
                lx += 0.028 + 0.013 * len(sname) + 0.04

        y_cursor = 0.0
        for i, it in enumerate(items):
            hl = it.get("highlight", False)
            start = 0.35 + i * stagger
            name_alpha = ease_out_cubic((t - start) / 0.4)
            if name_alpha > 0:
                ax.text(0, y_cursor + NAME_H * 0.45, it["name"],
                        va="center", ha="left",
                        fontsize=23, fontweight="bold" if hl else "normal",
                        color="white", alpha=name_alpha)

            vals = it["values"] if grouped else [it["value"]]
            for si, v in enumerate(vals):
                p = ease_out_cubic((t - start - si * 0.08) / bar_anim)
                color = (s_colors[si % len(s_colors)] if grouped
                         else it.get("color", "#E53935" if hl else "#9E9E9E"))
                y = y_cursor + NAME_H + si * BAR_H + BAR_H / 2
                val_now = v * p
                if p > 0:
                    ax.barh(y, BAR_FRAC, height=BAR_H * 0.62, color="white", alpha=0.07 * p)
                    ax.barh(y, (v / max_val) * BAR_FRAC * p, height=BAR_H * 0.62,
                            color=color, alpha=1.0 if (hl or grouped) else 0.85, zorder=3)
                    ax.text(1.0, y, f"{val_now:,.0f}",
                            va="center", ha="right",
                            fontsize=22, fontweight="bold" if hl else "normal",
                            color="white", zorder=4)
            y_cursor += block_h + ITEM_GAP

        if cfg.get("unit"):
            fig.text(0.93, 0.035, cfg["unit"], fontsize=16, color="#888888",
                     ha="right", alpha=title_alpha)

        fig.savefig(frames_dir / f"f{frame:05d}.png", transparent=True)
        plt.close(fig)

    return encode(frames_dir, fps, W, H, f"{out_name}_doc",
                  alpha=True, preview=False, green=True)


def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "chart_config.json"
    out_name = sys.argv[2] if len(sys.argv) > 2 else "chart"
    cfg, grouped, series, s_colors, max_val = load_cfg(cfg_path)

    outs = render_landscape(cfg, grouped, series, s_colors, max_val, out_name)
    if cfg.get("portrait", True):
        outs += render_portrait(cfg, grouped, series, s_colors, max_val, out_name)
    print("Done: " + ", ".join(outs))


if __name__ == "__main__":
    main()
