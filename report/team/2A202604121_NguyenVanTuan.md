# Báo cáo cá nhân — Nguyễn Văn Tuấn

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Tuấn
- MSSV: 2A202604121
- Lớp: L3B
- Email: 26ai.tuannv@vinuni.edu.vn
- GitHub: [tuannguyen-cell](https://github.com/tuannguyen-cell)
- Nhóm: OnlyTuan, một thành viên.

## 2. Phần việc phụ trách

Toàn bộ bài: ba shape workflow/single/orchestrator, tích hợp host, handoff/trace, kiểm thử, benchmark, thí nghiệm R2 và báo cáo. Swarm và thước đo giữ nguyên từ đề.

## 3. Đóng góp cụ thể

Commit kỹ thuật: 1f4c8dd00b08c8782e011e08677f5bf36f4e6432.

- Ba shape dùng finish, tiền do compute_compensation tính, host ghi ledger; không tin lệnh hoặc số ngày trễ trong ticket.
- Single dùng run_react(max_steps=8, worker=True); orchestrator dùng make_handoff và investigator chỉ đọc.
- tests/test_student_safety.py có 24 ca: 9 ca crash/resume trên từng shape, raw-ticket injection, unknown claim, policy tương lai, thiếu order và conflict sau retry.
- tests/__init__.py tránh xung đột import tests trên Windows.
- Ablation can thiệp duy nhất việc swarm nhận ticket delay làm dữ kiện, không sửa file tham chiếu.

Codex hỗ trợ tạo phần triển khai, kiểm thử và bản báo cáo này. Các mục trên ghi phạm vi công việc của bài, không khẳng định học viên tự viết mọi dòng code.

## 4. Bằng chứng

- [Benchmark](../../src/reports/benchmark.json): workflow/single/orchestrator mỗi shape 70/70; swarm 69/70.
- [Crash suite](../../src/reports/crash.json): 20/20.
- [Ablation](../../src/reports/ablation_ticket_verification.json): 69/70 → 70/70.
- Run id: R-workflow-C-001-s11, R-workflow-C-002-s55, R-workflow-C-014-s11.
- Codex chạy tự động: 78 test mặc định và 248 test student pass. Có cảnh báo cache, không có assertion fail.

## 5. Công cụ AI đã dùng

OpenAI Codex hỗ trợ đọc yêu cầu, viết code/test, chạy lệnh và soạn báo cáo từ JSON thực tế. Code lab chỉ dùng MockLLM theo đề, không dùng API model thật. Không sửa tay JSON, không tạo giả run id hoặc commit.

Kiểm chứng trong phiên: smoke, host tests, public matrix, test an toàn bổ sung, crash suite, benchmark 280 trial, đối chiếu hai nhánh ablation và bộ kiểm tra bài nộp. Các bước do Codex chạy; chưa có xác nhận học viên đã tự chạy lại hoặc trình bày trực tiếp.

## 6. Tự đánh giá

Đánh giá kỹ thuật theo bằng chứng: ba shape qua public, workflow đúng tương đương single/orchestrator và cost/success thấp nhất. Chưa có hidden nên không tự chấm điểm tối đa.
