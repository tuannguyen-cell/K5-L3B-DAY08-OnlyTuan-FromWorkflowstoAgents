# Decision record

- Shape chọn: workflow
- Commit hash: 1f4c8dd00b08c8782e011e08677f5bf36f4e6432
- Run id dẫn chứng: R-workflow-C-001-s11; R-workflow-C-002-s55; R-workflow-C-014-s11 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0–1.0 / 0.0; 70 trial public = 14 claim × 5 seed
- Cost per success (mô phỏng, VND): 28.8714285714
- Crash safety: 20/20 (src/reports/crash.json); thêm 9 test crash/resume trên 3 shape học viên đều pass
- Secret leak / approval bypass: không phát hiện vi phạm trong các assertion public và test bổ sung; chưa có số đếm hidden của giảng viên

## Vì sao shape này

Cùng 14 claim, seed 11/22/33/44/55, MockLLM, bảng giá và evaluator, workflow/single/orchestrator đều pass 70/70. Cost/success lần lượt 28.871429, 30.280000, 48.334286 VND mô phỏng; swarm là 49.566957 với 69/70 pass. Chọn workflow vì luật xử lý đã rõ và tuần tự, chưa thấy lợi ích chất lượng từ tăng tự chủ. Một thành viên cũng thuận tiện kiểm tra và duy trì luồng cố định.

## Có đáng đổi lấy multi-agent không

Chưa có bằng chứng đủ để chuyển trong setup này. Đánh giá lại nếu workload có các nguồn bằng chứng độc lập cần điều tra song song hoặc ticket cần suy luận ngữ nghĩa mà workflow không xử lý được. Khi đó đo lại chất lượng, chi phí, latency thật và cổng an toàn trên dữ liệu mới.

Ablation cùng swarm chỉ tắt việc dùng ticket delay ghi đè order: pass 69/70 → 70/70, pass^5 13/14 → 14/14. Đây là bằng chứng về kiểm chứng dữ kiện trong setup đã đo, không chứng minh mọi hệ multi-agent đều yếu hơn workflow.

## Trace và bằng chứng

Workflow ghi claim (found/has_order), order_scope (visible), quote, host_request, host_result, decision. Single thêm read_action; orchestrator thêm handoff đã qua make_handoff và investigator chỉ chứa tên tool/visible. Không dump ticket, principal, raw claim/order, parent_secret, header, phone, address, item hoặc internal_note. Không tạo file debug ngoài đường scanner.

Trace ghi trước lời gọi host để còn dấu vết khi crash; InjectedCrash lan ra ngoài. Mỗi lần trả về dùng finish để đọc effect/audit thật từ ledger và tạo trace mới. Trace không commit theo .gitignore, được tái tạo bằng các lệnh trong báo cáo nhóm.

## Giới hạn

Chưa có student_drop, chưa đo hidden hoặc xác nhận ngưỡng 0.75. MockLLM không phải model sản xuất; single dùng adapter quyết định theo trạng thái vì MockLLM không có API tool-call. Chi phí mô phỏng, latency unavailable. Số event trace khác nhau về độ chi tiết, không đại diện tốc độ. Hash trên chứa code/test/số liệu; commit báo cáo sau đó chỉ bổ sung tài liệu.
