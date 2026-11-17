# Gợi ý tự kiểm tra trước khi trình bày

Workflow được chọn vì trên public nó đúng 70/70 như single/orchestrator nhưng có cost/success mô phỏng thấp hơn. Không nói đã đạt hidden hoặc điểm tối đa.

| Câu hỏi | Ý cần giải thích |
| --- | --- |
| Vì sao không để model quyết tiền? | Luật tiền và approval cần xác định, kiểm bằng test. Ticket có thể nói dối. compute_compensation dùng order và policy hiệu lực. |
| Vì sao T14 proposal 150.000, refund 120.000? | Đã hoàn 30.000. Shape truyền quote 150.000; host trừ phần cũ. Trừ trước ở shape sẽ bị host trừ lần nữa. |
| Approval hỏng thì shape tự denied được không? | Quote dương vẫn gọi host để có audit policy_denied. Tự từ chối sẽ thiếu audit theo contract. |
| Crash sau tiền, trước checkpoint có trả hai lần? | Refund và audit commit cùng transaction, khóa refund:{claim_id} chống trùng. Resume lấy effect cũ; checkpoint không thay ledger. |
| Investigator được issue_refund không? | Không, handoff chỉ cấp tool đọc; orchestrator mới gọi host. |
| Trace loại field nào? | Không log raw ticket/claim/order, secret, header, phone, address, item, internal_note. Chỉ found/visible, quote, handoff allowlist, kết quả host. |
| Swarm sai chỗ nào? | C-002 seed55 lấy 5 ngày trong ticket thay vì 2 ngày trong order. Tắt ghi đè này sửa 69/70 → 70/70. |
| Vì sao matrix 248 pass mà swarm vẫn sai benchmark? | Test của swarm ở lỗi đã biết chủ động assert trial phải fail. Benchmark đo độ đúng nghiệp vụ. |
| Multi-agent luôn kém không? | Không. Lab nhỏ, MockLLM mô phỏng, shape khác cả prompt/số lời gọi. Chỉ kết luận cho setup đã đo. |
| Single là agent model thật không? | Không. MockLLM đề không có structured tool-call; adapter chọn tool theo observation, mô phỏng vòng ReAct bị giới hạn. |

Mở code, chạy lại lệnh trong báo cáo nhóm, đối chiếu JSON và xác nhận báo cáo cá nhân trước khi nộp. Tên lớp hiện tại L3B, mẫu đề ghi L3A: đối chiếu LMS trước khi đổi tên repo.
