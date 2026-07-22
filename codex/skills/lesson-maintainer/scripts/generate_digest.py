import os
import sys

def main():
    print("[Lesson Maintainer] 重新生成摘要層 (DIGEST.md)...")
    digest_content = """# Lesson Learnt Digest (摘要層)

> 這是供 Phase 0 冷啟動快速讀取的精華知識。僅收錄高頻 (出現 >3 次) 或升級為規則的教訓。

- [LL-001] (tags: security, jwt) JWT Token 未設定過期時間導致資安漏洞 -> 已強制寫入資安防禦規範。
- [LL-002] (tags: db, index) MongoDB 欠缺複合索引導致 Query Timeout -> 建議 DBA 提前審查 Schema。
"""
    
    # 假設存入 .agents/lessons_learned/DIGEST.md
    print("已生成假資料 DIGEST 供展示。")
    print(digest_content)

if __name__ == "__main__":
    main()
