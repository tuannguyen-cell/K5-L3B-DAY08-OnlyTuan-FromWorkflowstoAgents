# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- OnlyTuan: Nguyễn Văn Tuấn — 2A202604121 — L3B, nhóm một người.
- Commit kỹ thuật: 1f4c8dd00b08c8782e011e08677f5bf36f4e6432, trùng ADR.
- Có hỗ trợ Codex tạo code, kiểm thử, phân tích và soạn tài liệu; xem [báo cáo cá nhân](2A202604121_NguyenVanTuan.md) và [TEAM.md](../../TEAM.md).

## 2. Mục tiêu và cách tiếp cận

Xử lý claim bằng bốn kiến trúc trên cùng dữ liệu để chọn mức tự chủ thấp nhất đáp ứng nhiệm vụ. Nhóm một người thực hiện theo chuỗi: đọc contract → workflow → single → orchestrator → kiểm thử an toàn → benchmark → ADR. Swarm giữ nguyên làm đối chứng.

Nguồn sự thật là order đúng principal và policy hiệu lực tại ngày mô phỏng 2026-11-15. Ticket là dữ liệu không đáng tin. Hoàn ship khi đơn đã giao trễ ≥ 3 ngày; damage phải verified; cùng đủ điều kiện thì lấy số lớn hơn. Host kiểm approval đúng claim, cap theo đơn và chống ghi trùng.

## 3. Giải pháp

| Shape | Cách thực hiện | Ranh giới code / model |
| --- | --- | --- |
| Workflow | get_claim_view → kiểm order_id → lookup_order → compute_compensation → issue_refund → finish | Luồng cố định; MockLLM chỉ draft từ status/proposal do code tính. |
| Single | run_react(max_steps=8, worker=True); decide chọn lookup_order rồi compute_compensation dựa trên observation | Adapter theo trạng thái gọi MockLLM mỗi bước; MockLLM của đề không có API tool-call. Không mô tả đây là model thật tự lập kế hoạch. Host chỉ được gọi sau vòng lặp. |
| Orchestrator | make_handoff → run_readonly_investigators đọc order/policy/tính quote → orchestrator gọi host | Facts rỗng, tool allowlist; investigator không có tool ghi. Model plan/review/draft đều tính budget. |
| Swarm tham chiếu | Giữ nguyên peer/parse/draft và điểm yếu seed55 | Chỉ làm đối chứng, không chuyển điểm yếu sang code học viên. |

Mọi shape xử lý unknown claim → failed, thiếu order → needs_info, ngoài phạm vi/không có order → escalated, quote 0 → denied và không gọi host. Quote dương luôn truyền **đầy đủ** cho host, kể cả approval hỏng hoặc đơn đã hoàn; host mới tạo audit policy_denied và trừ phần đã hoàn. T14: quote 150.000, đã hoàn 30.000, host ghi 120.000; shape không trừ hai lần.

Truyền nguyên crash_at, không bắt InjectedCrash. Refund và refund_committed nằm trong một transaction; checkpoint không thay ledger. Replay cùng amount giữ effect cũ; amount khác → failed/amount_conflict. Kết nối đóng trong finally. finish đọc ledger/audit thật và ghi trace mới ở mọi nhánh trả về.

Trace chỉ ghi found/has_order, visible, quote, kết quả host và quyết định; single thêm tên tool đọc, orchestrator thêm handoff đã sanitize. Không ghi ticket, row nguyên bản, secret, header hoặc PII.

## 4. Kết quả

Nguồn: [benchmark.json](../../src/reports/benchmark.json). Bốn shape × 14 claim × 5 seed = 280 trial, SQLite mới mỗi trial, cùng model/seed/corpus/ngày policy/giá/evaluator.

| Shape | Pass | Pass^5 | Seed min–max | Variance | Cost/success, VND mô phỏng | Mean / p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 70/70 (100%) | 1.000000 | 1–1 | 0 | 28.871429 | 5.071429 / 6 |
| single | 70/70 (100%) | 1.000000 | 1–1 | 0 | 30.280000 | 6.857143 / 8 |
| orchestrator | 70/70 (100%) | 1.000000 | 1–1 | 0 | 48.334286 | 6.000000 / 7 |
| swarm | 69/70 (98.5714%) | 0.928571 | 0.928571–1 | 0.000816327 | 49.566957 | 2.800000 / 3 |

Pass nghĩa là đúng status, quote, ledger, audit và trace, không đồng nghĩa được hoàn tiền. Pass^5 là phần claim pass cả 5 seed; variance tính trên pass rate mỗi seed; cost/success là tổng cost mọi trial chia số trial pass. Steps là số event trace với mức chi tiết khác nhau giữa shape, không dùng suy latency.

- Smoke: pass, Python 3.13.3, Windows AMD64.
- Host và test bổ sung: **78 passed, 248 deselected**; gồm 24 ca mới.
- Ma trận student: **248 passed, 78 deselected**. Riêng swarm/C-002/seed55, test chủ động assert trial phải fail; benchmark vẫn là 69/70.
- [Crash suite](../../src/reports/crash.json): **20/20**, chủ yếu kiểm host và có một ca swarm. Thêm **9 test** = 3 shape học viên × 3 cửa sổ crash/resume, đều pass.
- Public và test bổ sung không phát hiện leak/bypass trong phạm vi assertion; chưa có student_drop hoặc hidden, không khẳng định ngưỡng hidden đã đạt.

Chọn workflow: độ đúng bằng single/orchestrator, chi phí mô phỏng thấp nhất. [ADR](decision_adr.md) ghi điều kiện đổi quyết định. [Research card](research_card.md): chỉ tắt việc swarm lấy ticket delay ghi đè order, sửa đúng C-002/seed55, 69/70 → 70/70.

## 5. Khó khăn và cách xử lý

1. Pytest đầu gặp AttributeError: module 'torch' has no attribute 'save'. Import tests.conftest bị trỏ sang package tests của Ultralytics trên máy. Thêm src/tests/__init__.py để nhận package cục bộ; không sửa test gốc hoặc host.
2. Sandbox chặn thư mục tạm pytest-of-…, gây WinError 5 trước khi test chạy. Sau khi được cấp quyền, chạy lại ngoài sandbox và có kết quả ở mục 4. Cảnh báo không tạo được .pytest_cache vẫn còn nhưng không ảnh hưởng assertion; có thể dùng -p no:cacheprovider.
3. T13/T14 dễ bị trừ refund cũ hai lần. Giữ proposal đầy đủ, để host tính phần còn lại; public matrix kiểm cả hai trường hợp.

## 6. Tổng hợp đóng góp

Nguyễn Văn Tuấn phụ trách toàn bộ bài trong nhóm một người. Commit kỹ thuật chứa ba shape, test và số liệu thực nghiệm; commit sau bổ sung tài liệu. Codex hỗ trợ thực hiện và kiểm chứng tự động, được khai báo trong báo cáo cá nhân; không tự gán trải nghiệm hoặc xác nhận học viên đã trực tiếp chạy các lệnh.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; cost mô phỏng, latency unavailable. Public nhỏ và có nhãn biết trước; hidden do giảng viên chấm riêng. Bốn shape khác cả prompt và số lời gọi nên không cô lập tác động topology. Ablation cùng swarm xét riêng một cơ chế kiểm chứng. Với triển khai thật cần dữ liệu mới, model có structured tool calls, latency thật và kiểm tra đồng thời/lỗi hạ tầng.

## 8. Tài liệu tham khảo

- Tài liệu đề: [business rules](../../docs/business_rules.md), [contracts](../../docs/contracts.md), [metrics](../../docs/metrics.md), [rules](../../RULES.md).
- Cemri và cộng sự (2025), [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657), dùng cho research card. Không sử dụng code ngoài repo đề.

## Phụ lục: tái lập

Tại src/, Python 3.11–3.13 đã cài requirements.txt, chạy lần lượt:

1. python -m lab8.smoke
2. python -m pytest -q
3. python -m pytest -q -m student -o addopts=
4. python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
5. python -m lab8.crash_test --count 20 --out reports/crash.json
6. python -m bonus.verification_ablation
7. python -m lab8.check_submission

Không cần API key hay internet. Trace được tạo lại, không commit; JSON bằng chứng do công cụ sinh. 
