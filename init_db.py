import sqlite3

# データベース接続（なければ自動作成）
conn = sqlite3.connect('kakeibo.db')
cur = conn.cursor()

# テーブル作成
cur.execute('''
CREATE TABLE IF NOT EXISTS kakeibo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    oshi_name TEXT NOT NULL,     -- 推しの名前
    category TEXT NOT NULL,      -- カテゴリ（例：グッズ・チケット）
    expense INTEGER DEFAULT 0,   -- 出金
    income INTEGER DEFAULT 0,    -- 入金
    memo TEXT,                   -- メモ
    date TEXT NOT NULL           -- 日付（YYYY-MM-DD）
);
''')

conn.commit()
conn.close()
print("✅ データベースを初期化しました！")
