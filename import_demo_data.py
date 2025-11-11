"""
Script để import dữ liệu demo vào MySQL
Chạy file này một lần để tạo dữ liệu test
"""

import json
import mysql.connector
from datetime import datetime

# Cấu hình database
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'todo_app_mvc'
}

def import_demo_data():
    """Import dữ liệu từ demo_notes.json vào MySQL"""
    
    # Đọc file JSON
    print("Đọc dữ liệu demo...")
    with open('data/demo_notes.json', 'r', encoding='utf-8') as f:
        demo_notes = json.load(f)
    
    print(f"Tìm thấy {len(demo_notes)} ghi chú demo.")
    
    # Tạo database nếu chưa tồn tại
    print("Kết nối MySQL và tạo database...")
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute(f"USE {DB_CONFIG['database']}")
    
    # Tạo bảng notes
    print("Tạo bảng notes...")
    cursor.execute("DROP TABLE IF EXISTS notes")
    cursor.execute("""
        CREATE TABLE notes (
            note_id VARCHAR(36) PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            category VARCHAR(100),
            priority VARCHAR(50),
            is_completed BOOLEAN,
            is_important BOOLEAN,
            due_date DATE,
            reminder TEXT,
            attachments TEXT,
            created_at DATETIME,
            updated_at DATETIME
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """)
    conn.commit()
    
    # Xóa dữ liệu cũ (nếu có)
    print("Xóa dữ liệu cũ...")
    cursor.execute("DELETE FROM notes")
    conn.commit()
    
    # Insert dữ liệu mới
    print("Insert dữ liệu demo...")
    success_count = 0
    
    for note in demo_notes:
        try:
            # Convert attachments list to JSON string
            attachments_json = json.dumps(note.get('attachments', []), ensure_ascii=False)
            
            # Parse datetime
            created_at = datetime.fromisoformat(note['created_at'])
            updated_at = datetime.fromisoformat(note['updated_at'])
            
            # Parse due_date
            due_date = note.get('due_date')
            
            cursor.execute("""
                INSERT INTO notes 
                (note_id, title, content, category, priority, is_completed, 
                 is_important, due_date, reminder, attachments, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                note['note_id'],
                note['title'],
                note['content'],
                note['category'],
                note['priority'],
                note['is_completed'],
                note['is_important'],
                due_date,
                note.get('reminder'),
                attachments_json,
                created_at,
                updated_at
            ))
            
            success_count += 1
            print(f"  ✓ Imported: {note['title']}")
            
        except Exception as e:
            print(f"  ✗ Lỗi khi import '{note['title']}': {e}")
    
    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Hoàn tất! Đã import {success_count}/{len(demo_notes)} ghi chú vào database.")
    print(f"{'='*60}")

if __name__ == "__main__":
    try:
        import_demo_data()
    except Exception as e:
        print(f"Lỗi: {e}")
        print("\nLưu ý: Đảm bảo MySQL đang chạy và thông tin kết nối đúng.")
        print("Bạn có thể sửa DB_CONFIG trong file này nếu cần.")
