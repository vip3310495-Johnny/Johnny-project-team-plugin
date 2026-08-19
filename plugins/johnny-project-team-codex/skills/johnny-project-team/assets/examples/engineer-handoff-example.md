# Wave1_M01_Engineer Hand off — Review Cycle 1

> 這是填寫深度範例，路徑、命令、hash 與結果均為示意，不是可直接沿用的 evidence。

## 識別資料

- Ticket／Milestone：M01
- Wave：Wave1
- Review cycle：1
- Branch：`codex/milestone-M01`
- Commit：`7c4f6c1`
- Subject tree：`a93e60b`
- Context Pack 版本／路徑：`PM/Context/M01-v2.md`

## 完成範圍

- 本次完成的 observable outcomes：有效購物車可透過公開 API 建立訂單；庫存不足時回傳明確錯誤且不建立訂單。
- 明確未處理的 non-goals：付款扣款、優惠券與管理後台。
- CONTROLLED Change Notice（如有）：None；未改變已核准 contract。

## 修改明細

| 路徑／元件 | 原問題或先前行為 | 修改內容 | 修改理由／對應需求 | 相容性與風險 |
|---|---|---|---|---|
| `src/orders/service.py` | 尚無建立訂單流程 | 新增 `create_order()` 並透過 inventory port 預留庫存 | M01 outcome 1 | 保持既有 error envelope；交易 rollback 為主要風險 |
| `src/orders/api.py` | 無 `POST /orders` | 接上 service 並轉譯 domain error | M01 public interface | 新增 endpoint，不修改既有 route |
| `src/tests/orders/` | 無 M01 回歸測試 | 新增成功、庫存不足與 rollback 測試 | 保護 M01 contract | 測試只經公開 API 與測試 DB |

## 規則與 TDD 證據

- ECC selection hash：`sha256:example-selection-hash`
- 已讀取的 ECC rules：`common/testing.md`、`python/testing.md`、`python/fastapi.md`
- TDD cycle evidence 路徑：`Engineer/evidence/M01_R1_tdd-cycles.md`
- 永久測試路徑：`src/tests/orders/test_create_order.py`
- 預期 RED 摘要與 evidence（不得列入下方非預期失敗）：三輪 RED 分別證明缺少 endpoint、庫存錯誤未轉譯、交易未 rollback；詳見 cycle evidence。

## 已執行測試

| 類型／範圍 | 驗證目的 | 可重跑命令 | 結果 | Evidence |
|---|---|---|---|---|
| Integration／orders | 成功、失敗與 rollback 行為 | `pytest src/tests/orders -q` | PASS，8 tests | `Engineer/evidence/M01_R1_pytest.txt` |
| Coverage／orders | 避免未測分支 | `pytest src/tests/orders --cov=src/orders --cov-report=term` | PASS，91% | `Engineer/evidence/M01_R1_coverage.txt` |
| Lint | 靜態品質 | `ruff check src` | PASS | `Engineer/evidence/M01_R1_ruff.txt` |
| Type-check | 型別邊界 | `mypy src/orders` | PASS | `Engineer/evidence/M01_R1_mypy.txt` |
| Build／Acceptance | 套件可建置且 API contract 通過 | `python -m build && pytest src/tests/acceptance/test_orders.py -q` | PASS | `Engineer/evidence/M01_R1_acceptance.txt` |

## Smoke test 閘門

- 交付類型：Service
- Smoke／最接近 probe 的關鍵路徑：啟動本機 API，以有效購物車建立一筆訂單並讀回相同訂單。
- 測試環境與必要前置條件：Python 3.13、SQLite temporary DB、測試 inventory adapter；不使用 production credentials。
- 可重跑命令／操作步驟：`python src/scripts/smoke_orders.py --database :memory:`
- 預期結果：exit code 0，輸出 `ORDER_SMOKE_PASS`，訂單狀態為 `created`。
- 實際結果：exit code 0，`ORDER_SMOKE_PASS order_id=example-42 status=created`。
- Evidence：`Engineer/evidence/M01_R1_smoke.txt`
- Verdict：PASS

## 使用工具與依賴

| 工具／版本或來源 | 用途 | 實際用法／命令 | 產出或副作用 |
|---|---|---|---|
| Python 3.13 | runtime 與測試 | `python -m pytest ...` | 產生測試輸出；無產品檔案副作用 |
| pytest 8.4 | 行為與回歸測試 | `pytest src/tests/orders -q` | 8 tests PASS |
| ruff 0.12 | lint | `ruff check src` | 無修改，PASS |
| mypy 1.17 | type-check | `mypy src/orders` | 無修改，PASS |

- 新增／移除／升級的依賴與理由：新增既有 lockfile 已允許的 `httpx` test extra，用於公開 API integration test；未加入 runtime dependency。

## 非預期失敗紀錄

| 階段 | 命令／動作 | 觀察到的失敗 | 根因 | 處理方式 | 最終狀態／Evidence |
|---|---|---|---|---|---|
| Integration test | `pytest src/tests/orders -q` | Windows 上第二次執行出現 SQLite database locked | fixture 未關閉 connection | fixture 改用 context manager 並在 teardown 明確 close | RESOLVED；連續重跑 3 次 PASS，見 `Engineer/evidence/M01_R1_pytest-repeat.txt` |
| Build | `python -m build` | package 未包含新 module | package discovery 只列舊目錄 | 修正 `pyproject.toml` discovery 設定並新增 build smoke | RESOLVED；見 `Engineer/evidence/M01_R1_build.txt` |

## 流程觀察

| 規則／context／工具問題 | 對流程的影響 | 暫時處理 | 建議改善 |
|---|---|---|---|
| Context Pack 未列 Windows DB lock 風險 | 第一次 integration 重跑失敗，多花一次診斷循環 | 補 teardown 與重跑 evidence | 未來含 SQLite 的 Ticket 在 Context Pack 加入資源釋放檢查 |

## 交付注意事項

- 已知限制與剩餘風險：尚未驗證 production database；屬部署環境範圍，不在 M01。
- 建議 TDD DQA 優先檢查項目：庫存不足時訂單與 reservation 必須同時 rollback。
- Rollback 方法：revert commit `7c4f6c1`；本 Ticket 無 schema migration。

## PM 接件

- Engineer 結論：READY_FOR_PM
- Blocker（若有）：None
- 本報告路徑：`Engineer/Wave1_M01_R1_Engineer_Hand_off.md`
