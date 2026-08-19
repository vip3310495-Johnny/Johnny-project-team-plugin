# Phase 5：本輪封存、交接與 retrospective

Phase 5 結束的是目前實作輪次，不是永久結束專案。產品建構已完成；本階段不得改變
產品行為。

## Handover

- PM consolidates `Architect/As_Built_Architecture.md`, Phase 4 completion
  evidence, decisions, and Lessons Learned.
- Create `Project_Handover_Manual.md` covering setup, build, tests, deployment,
  monitoring, troubleshooting, permissions, dependencies, maintenance, and
  emergency procedures.
- Record known limitations, technical debt, backlog, and ownership without
  rewriting approved Phase 4 history.

## Scope-quality retrospective

Review which FIXED items were too prescriptive or too broad, which
classifications changed, which compatibility failures occurred, and which
templates, gates, or heuristics should improve next time. Separate Contract
Violations from Process/Documentation Defects and update Lessons Learned.

## Close

寫入本輪最後一筆 Master Log，包含 handover、As-Built report、final commit 與 open
items。確認沒有未解決的 Milestone、DQA escalation、credential handoff 或外部相依項目。
關閉 active child agents、釋放 temporary resources，並封存本輪 project state。

若 CEO 要開啟下一輪實作，PM 必須先確認本節完成，取得 CEO 明確 approval，再執行：

`python scripts/johnny_phase_gate.py --project <repo> --to-phase 0 --approval "<CEO approval>"`

這是唯一允許的 restart transition。它保留 audit history、Lessons Learned、handover 與
As-Built 文件，清除本輪 execution policy、Phase 4 execution 與 prerequisite evidence，
並使下一輪回到 Phase 0 的需求探索；不得直接修改 state 檔案。
