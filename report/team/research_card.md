# Research card

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 — Failure taxonomy: kiểm chứng dữ kiện trong swarm |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri và cộng sự, 2025, Why Do Multi-Agent LLM Systems Fail?, NeurIPS Datasets and Benchmarks; nghiên cứu thực nghiệm: https://arxiv.org/abs/2503.13657 |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | MAST phân loại 14 dạng lỗi thành 3 nhóm: thiết kế hệ thống, lệch phối hợp giữa agent và kiểm chứng tác vụ. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nguồn khảo sát trace từ 7 framework MAS và các model/tác vụ trong nghiên cứu, không trực tiếp đo LogiX-VN hay MockLLM. Gán lỗi seed55 vào task verification là diễn giải của bài lab. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Chỉ tắt quyền dùng parsed ticket delay ghi đè order sẽ sửa T02/seed55: pass 69/70 → 70/70, pass^5 13/14 → 14/14, không tăng model calls. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cùng swarm reference, MockLLM, prompt, danh sách tool, 14 claim public, seed 11/22/33/44/55, giá và evaluator. Chỉ đổi accept_ticket_delay_override qua scoped patch parse_delay_days trả None; không sửa file swarm, host, fixture hay thước đo. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Ticket nói trễ 5 ngày, order ghi 2 ngày. Đo trial_pass theo ledger/nhãn public, pass_rate, pass_5, seed_variance, cost_per_success_vnd, model/tool calls và trial đổi kết quả. |

## Kết quả ablation

- Lệnh đã chạy tại src/: python -m bonus.verification_ablation
- File report: src/reports/ablation_ticket_verification.json, hai nhánh baseline và verified, sinh qua run_benchmark, không sửa JSON bằng tay.
- Run id: R-swarm-C-002-s55 trong mỗi nhánh. Run id xác định theo hàm đề bài nên phải đọc kèm tên nhánh; trace trên đĩa có thể được lần chạy sau ghi lại.

| Metric | Baseline | Verified |
| --- | ---: | ---: |
| Trial / pass | 70 / 69 | 70 / 70 |
| Pass rate | 0.985714286 | 1.000000000 |
| Pass^5 | 0.928571429 | 1.000000000 |
| Seed min–max | 0.928571429–1.0 | 1.0–1.0 |
| Seed variance | 0.000816327 | 0 |
| Cost/success, VND mô phỏng | 49.566956522 | 48.715714286 |
| Model calls trung bình | 3.0 | 3.0 |
| Tool calls trung bình | 4.657142857 | 4.642857143 |

Hypothesis đúng trên public: chỉ C-002/seed55 từ fail thành pass, các trial khác giữ kết quả. Tool calls giảm do không tính lại quote sau ghi đè delay; đó là hệ quả của can thiệp, danh sách tool vẫn giữ nguyên.

So sánh A/B/C/D không phải ablation thuần topology vì khác cả prompt và số lời gọi. Thí nghiệm này xét riêng một cơ chế trong cùng swarm. Không xin điểm bonus từ thí nghiệm.

Giới hạn: điểm yếu swarm đã được đề công bố, đây là kiểm chứng cơ chế trên ví dụ biết trước, không phải phát hiện mới. Chưa suy rộng sang hidden hay model thật. Latency unavailable.

Nguồn đã kiểm chứng: [NeurIPS 2025 proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html).
