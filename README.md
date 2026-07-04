# tinhte-charts

Sửa **một file JSON** duy nhất → tự động ra:
1. Video chart động (nền trong suốt + nền xanh) cho team media chèn vào video review.
2. Link chart web (animation chạy khi cuộn tới) để chèn vào bài viết.

## Setup một lần

1. Push toàn bộ repo này lên GitHub (branch `main`).
2. Bật GitHub Pages: **Settings → Pages → Source: Deploy from a branch → main / (root)**.
3. Kiểm tra `https://<username>.github.io/tinhte-charts/chart.html` hiện chart demo là xong.

## Quy trình mỗi bài review (ai cũng làm được, chỉ cần trình duyệt)

1. Vào thư mục **`data/`** trên GitHub web.
2. Copy file `geekbench6.json` thành file mới (nút **Add file → Create new file**, hoặc mở file cũ → **Edit** → đổi số liệu → **Commit changes** nếu muốn ghi đè). Đặt tên không dấu, ví dụ `antutu-iphone17.json`.
3. Sửa số liệu:

```json
{
  "title": "Geekbench 6 — Multi-core",
  "subtitle": "Điểm càng cao càng tốt",
  "unit": "điểm",
  "items": [
    { "name": "Snapdragon 8 Elite", "value": 10250, "color": "#E53935", "highlight": true },
    { "name": "Apple A18 Pro",      "value": 10080, "color": "#9E9E9E" }
  ]
}
```

Máy nào là nhân vật chính của bài thì để `"highlight": true` và màu riêng, các máy còn lại để `#9E9E9E`.

4. Bấm **Commit changes**. GitHub Actions tự chạy (~2–3 phút), theo dõi ở tab **Actions**.
5. Lấy kết quả ở tab **Releases** — mỗi chart là một release, gồm:

| File | Ai dùng | Cách dùng |
|---|---|---|
| `*_alpha.mov` | Team media (Premiere / Final Cut / DaVinci) | Kéo lên track video NẰM TRÊN footage. Nền tự trong suốt, không cần key. |
| `*_greenscreen.mp4` | Team media (CapCut) | Kéo lên layer trên → Cutout → **Chroma Key** → chấm màu xanh. |
| `*_preview.mp4` | Mọi người | Xem thử animation trước khi dựng. |
| Phần mô tả release | Editor | Chứa sẵn **link chart web** + mã iframe để chèn vào bài viết. |

Link nhúng cũng hiện trong **Summary** của run Actions.

## Chèn chart web vào bài Tinh tế

Nhờ dev thêm một media site mới trong XenForo admin (giống cách Infogram đã được thêm):

- URL match: `*.github.io/tinhte-charts/chart.html?d=*`
- Embed template: `<iframe src="{$url}" width="100%" height="420" frameborder="0" loading="lazy" scrolling="no"></iframe>`

Sau đó chỉ cần dán link từ release notes vào bài như dán link Infogram.

## Tuỳ chỉnh trong JSON

| Khoá | Ý nghĩa | Mặc định |
|---|---|---|
| `duration` | thời gian animation (giây, video) | 4.0 |
| `hold` | giữ khung cuối (giây, video) | 1.5 |
| `stagger` | độ trễ giữa các thanh (giây) | 0.18 |
| `fps`, `width`, `height` | thông số video | 30, 1920, 1080 |
| `accent` | màu thanh highlight (web chart) | `#E53935` |
| `replayOnScroll` | web chart chạy lại mỗi lần cuộn tới | false |
| `decimals` | số chữ số thập phân (web chart) | 0 |

## Chạy tay trên máy (không bắt buộc)

```bash
pip install matplotlib numpy   # cần thêm ffmpeg trong PATH
python3 render_chart.py data/geekbench6.json geekbench6
python3 make_embed.py data/geekbench6.json https://<username>.github.io/tinhte-charts/chart.html
```
