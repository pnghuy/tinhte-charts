# tinhte-charts — ghi chú cho Claude

Repo làm chart benchmark cho bài review Tinh tế. Schema JSON, cách render và các lỗi thường gặp đều nằm trong README.md, đọc README trước khi tạo hoặc sửa data.

## Tạo data cho bài mới
- Mỗi máy một folder `data/YYYY-MM-ten-may/`, mỗi bài test một file `.json`.
- Tên file viết thường, dùng gạch ngang, không dấu, luôn có đuôi `.json`.
- Có `series` thì là chart nhóm (`values`), không có thì là chart đơn (`value`).
- Máy đang review đặt `"highlight": true`. Tên ghi kèm chip trong ngoặc, ví dụ `HP OmniBook X Flip 14 (Ultra 5 325)`.
- Không để dấu phẩy sau item cuối cùng. Tạo xong thì kiểm tra lại bằng `python3 -c "import json;json.load(open('<file>'))"`.

## Thứ tự máy trong chart (áp dụng cho mọi bài)
- Máy đang review luôn đứng đầu.
- Các máy so sánh xếp giảm dần theo điểm chính: chart đơn xếp theo `value`; chart nhóm xếp theo series cuối (ví dụ Multi-core); pin xếp theo thời lượng.
- Với bài test mà số thấp mới tốt (nhiệt độ, độ ồn, thời gian xuất video…), xếp tăng dần, máy tốt nhất đứng trước.
- Thứ tự này áp dụng đồng nhất cho mọi chart trong cùng một bài.

## Ghi nguồn (`source`)
- Chỉ ghi `Nguồn: Tinhte.vn đo thực tế` khi **mọi** số trong chart do Tinh tế tự đo.
- Có số lấy từ nơi khác thì KHÔNG dùng câu "Tinhte.vn đo thực tế". Ghi đúng nguồn của từng phần, ví dụ:
  `Nguồn: Tinhte.vn; đa nhân OmniBook X Flip 14 theo Geekbench Browser`
- Nếu toàn bộ số đều lấy từ ngoài, chỉ ghi nguồn ngoài đó.

## Render
- **Ảnh JPG để chèn bài** (nhanh, chạy ngay trên máy):
  `python3 render_chart.py data/<folder>/<file>.json <ten-output> --still-only`
- **Zip video cho team dựng phim:** người dùng tự bấm GitHub Actions → Render chart, input `file` là folder hoặc file. Chỉ chạy `gh workflow run render.yml -f file=data/<folder>` khi người dùng yêu cầu rõ.
- Không bật auto-render khi push.

## Khi viết bài có chart
- Đặt placeholder `[Ảnh: <ten-output>.jpg]` đúng chỗ cần biểu đồ trong bài, rồi gửi kèm file JPG.

## Khi gặp lỗi
- JSON hoặc render lỗi thì báo lại cho người dùng, không tự thử sửa quá 2 lần.
