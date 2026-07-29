---
name: 5w1h-grill-me
description: 結合 5W1H 框架 (Why, Who, Where, What, When, How to do) 的專業需求深度盤問技能 (Grill-Me)。當使用者提出模糊需求、規劃新功能、啟動專案 Phase 0 或需要進行需求反覆盤問與收斂時觸發。
---

# 5W1H Grill-Me 需求深度盤問技能指南

> **【核心原則】**：反通靈與強勢需求收斂。嚴禁盲目寫碼，強制透過 3-Pass 盤問協定收斂 5W1H 規格。

---

## 🎯 5W1H 專業盤問矩陣

| 維度 | 專業領域 (Domain Focus) | 盤問與收斂焦點 (Grill & Convergence Focus) |
| :--- | :--- | :--- |
| **Why** | **商業動機與意圖 (Intent & Pain Points)** | 核心目的、欲解決痛點、非目標邊界 (Non-goals)。 |
| **Who** | **目標客群與角色 (Personas & RBAC)** | 目標使用者、角色權限矩陣 (RBAC Matrix)。 |
| **Where** | **部署與執行拓撲 (Topology)** | 部署環境 (GCP/AWS/On-Prem)、運行載體 (Web/App/Desktop)。 |
| **What** | **美學與核心功能 (UI Aesthetics & Features)** | UI/UX 視覺導向、Must-have 核心功能、標竿競品 (Benchmark Reference)。 |
| **When** | **專案量體與動態觸發 (Scale & Event Triggers)** | 交付時程/專案規模、When-Action 事件觸發條件 (Event-Driven Triggers)。 |
| **How** | **技術選型與強勢提案 (Tech Stack & Proposals)** | 指定技術棧、防通靈強勢單選提案 (Anti-Guessing Strong Proposals)。 |

---

## 🔄 3-Pass 盤問協定 (3-Pass Grill Protocol)

1. **Pass 1 (戰略大局)**：掃描 5W1H 全局輪廓，確立專案規模與商業動機。
2. **Pass 2 (死角補強)**：精準補強視線死角 (Event Triggers, UI 美學, RBAC)。當使用者未定時，提供 **2-3 個強勢單選方案**。
3. **Pass 3 (收斂簽核)**：產出 `PM/5W1H_Requirement_Digest.md` 摘要表，請求 `/approve` 簽核。

---

## 📄 產出規格：`PM/5W1H_Requirement_Digest.md`

```markdown
# 5W1H 需求摘要表 (Requirement Digest)

- **Why (Intent)**: [商業目的 / Pain Points]
- **Who (Personas & RBAC)**: [主要使用者 / 權限矩陣]
- **Where (Topology)**: [部署目標 / 執行環境]
- **What (Aesthetics & Features)**: [視覺風格 / Core Features / Benchmark]
- **When (Scale & Triggers)**: [專案規模 / When-Action 觸發條件]
- **How (Tech Stack)**: [技術選型 / 架構樣式]
```
