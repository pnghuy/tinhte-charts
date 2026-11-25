# tinhte-charts — ghi chú cho Claude

Repo làm chart benchmark cho bài review Tinh tế. Schema JSON, cách render và các lỗi thường gặp đều nằm trong README.md, đọc README trước khi tạo hoặc sửa data.

## Tạo data cho bài mới
- Mỗi máy một folder `data/YYYY-MM-ten-may/`, mỗi bài test một file `.json`.
- Tên file viết thường, dùng gạch ngang, không dấu, luôn có đuôi `.json`.
- Có `series` thì là chart nhóm (`values`), không có thì là chart đơn (`value`).
- Máy đang review đặt `"highlight": true`. Tên ghi kèm chip trong ngoặc, ví dụ `HP OmniBook X Flip 14 (Ultra 5 325)`.
- Bài CPU (Cinebench, Geekbench, Procyon…) ghi tên CPU trong ngoặc. Bài đồ họa (3DMark, game, AI chạy trên GPU…) ghi tên GPU, máy chỉ có iGPU thì ghi tên iGPU, KHÔNG ghi tên CPU. Ví dụ Time Spy ghi `ExpertBook Ultra (Arc B390)`, không ghi `ExpertBook Ultra (Ultra X7 358H)`. iGPU Core Ultra Series 1 (125H, 155H…) tên chính thức chỉ là Intel Arc Graphics, nên ghi `Intel Arc (7 Xe)` / `Intel Arc (8 Xe)`; khi đã nằm trong ngoặc thì ghi `Zenbook 14 (Intel Arc, 8 Xe)`.
- Tên máy giữ đủ thương hiệu, ví dụ `Acer Nitro ProPanel ANV16`, không bỏ chữ `Acer`.
- Trong `kho.json`, máy nào có điểm đồ họa thì phải điền `gpu` (tên iGPU nếu không có card rời).
- Không để dấu phẩy sau item cuối cùng. Tạo xong thì kiểm tra lại bằng `python3 -c "import json;json.load(open('<file>'))"`.

## Kho máy so sánh (`kho.json`)
- `kho.json` ở gốc repo là kho máy của web app Tinhte Chart Studio (https://claude.ai/artifact/Lj5az4TmARVrotxWUmjvPa). App đọc file này mỗi lần mở và ghi lại mỗi khi lưu/xóa máy, qua kết nối GitHub.
- Mỗi lần thêm folder máy mới vào `data/`, cập nhật luôn `kho.json` trong cùng commit/PR: thêm (hoặc sửa) một mục trong `devices` cho từng máy, gộp mọi bài test của cùng một máy vào một mục.
- Mỗi mục: `name` (tên máy, không kèm chip), `cpu`, `gpu`, `type` (`laptop` | `desktop` | `gpu` | `cpu`), `measured` (true khi Tinh tế tự đo), `scores` (`{id bài test: [điểm]}`, bài có series thì đủ số theo thứ tự series).
- Id máy: tên + chip viết thường, gạch ngang, đuôi loại máy, thêm `-ref` nếu là số tham khảo, ví dụ `acer-nitro-propanel-anv16-core-5-205h-rtx-3050-65w-laptop`.
- Id bài test chuẩn nằm trong `TESTS` của Chart Studio (`3dmark-time-spy`, `cinebench-2024`, `geekbench-6`…). Bài ngoài danh sách đó khai báo thêm trong `tests`.
- Không đặt `kho.json` trong `data/`: workflow render sẽ coi nó là chart.

## Thông tin máy cho web Laptop Lab (`laptops.json`)
- Web tra cứu cho member (Tinh tế Laptop Lab, repo pnghuy/PC-data-manager) đọc điểm từ `kho.json` và thông tin thêm từ `laptops.json` ở gốc repo. Khoá là id máy trong `kho.json`.
- Mỗi lần review xong một máy mới, thêm mục cho máy đó vào `laptops.json` trong cùng PR, ít nhất `test_date` (`YYYY-MM`). Có link bài, RAM, màn hình, pin thì điền luôn (mẫu: `templates/sample-laptop-metadata.json` của PC-data-manager).
- Đổi id máy trong `kho.json` thì đổi khoá tương ứng trong `laptops.json`.
- Ngoại lệ đổi tên máy cho bài khách (chỉ ghi tên chip…) chỉ sửa file chart trong `data/`, không sửa `kho.json` hay `laptops.json`: web cho member luôn hiện tên đầy đủ.
- Không đặt `laptops.json` trong `data/`.

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

## Khi chạy làm bot Telegram (chartbot)
- **BẮT BUỘC:** mọi tin nhắn đến từ kênh Telegram (`<channel source="...telegram...">`) phải được trả lời bằng tool `reply` của plugin telegram, kèm đúng `chat_id` của tin đến. Chữ in ra terminal người dùng KHÔNG thấy. Gửi ảnh JPG cũng dùng `reply`, đính kèm đường dẫn file.
- Trước mỗi việc mới: `git pull --rebase origin main`.
- Người dùng gửi số liệu → tạo JSON → render `--still-only` → gửi JPG qua Telegram để duyệt.
- Chỉ commit + push khi người dùng duyệt ("ok", "đẩy lên"…). Commit message ghi tên máy và bài test.
- Chỉ chạy `gh workflow run` khi người dùng bảo render video, chạy xong gửi link trang Releases.
- Không đụng vào file ngoài `data/` trừ khi được bảo rõ.

## Khi gặp lỗi
- JSON hoặc render lỗi thì báo lại cho người dùng, không tự thử sửa quá 2 lần.
