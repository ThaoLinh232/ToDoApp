"""
Script migrate database từ cấu trúc cũ sang cấu trúc mới (normalized)
"""

import mysql.connector
import json
from datetime import datetime

# Cấu hình database
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'todo_app_mvc',
    'charset': 'utf8mb4'
}

def migrate_database():
    """Migrate dữ liệu từ cấu trúc cũ sang mới"""
    
    print("=" * 70)
    print("DATABASE MIGRATION - Chuyển sang cấu trúc normalized")
    print("=" * 70)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 1. Kiểm tra xem bảng notes cũ có tồn tại không
        cursor.execute("SHOW TABLES LIKE 'notes'")
        if not cursor.fetchone():
            print("❌ Không tìm thấy bảng notes. Chạy app.py để tạo database mới.")
            return
        
        # 2. Backup dữ liệu cũ
        print("\n📦 Backup dữ liệu từ bảng notes cũ...")
        cursor.execute("SELECT * FROM notes")
        old_notes = cursor.fetchall()
        print(f"   Tìm thấy {len(old_notes)} ghi chú.")
        
        if len(old_notes) == 0:
            print("✅ Không có dữ liệu cần migrate.")
            return
        
        # 3. Đổi tên bảng notes cũ thành notes_backup
        print("\n🔄 Đổi tên bảng notes → notes_backup...")
        cursor.execute("DROP TABLE IF EXISTS notes_backup")
        cursor.execute("RENAME TABLE notes TO notes_backup")
        conn.commit()
        
        # 4. Tạo cấu trúc database mới
        print("\n🏗️  Tạo cấu trúc database mới...")
        
        # Import NoteRepository để tạo tables
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from models.NoteRepository import NoteRepository
        
        # Khởi tạo sẽ tự động tạo các bảng mới
        repo = NoteRepository()
        
        print("\n📥 Migrate dữ liệu vào cấu trúc mới...")
        
        # 5. Lấy mapping categories và priorities
        cursor.execute("SELECT category_id, category_name FROM categories")
        categories_map = {row['category_name']: row['category_id'] for row in cursor.fetchall()}
        
        cursor.execute("SELECT priority_id, priority_name FROM priorities")
        priorities_map = {row['priority_name']: row['priority_id'] for row in cursor.fetchall()}
        
        # 6. Insert notes vào bảng mới
        success_count = 0
        for old_note in old_notes:
            try:
                # Map category và priority
                category_id = categories_map.get(old_note.get('category'), categories_map.get('Cá nhân'))
                priority_id = priorities_map.get(old_note.get('priority'), priorities_map.get('Bình thường'))
                
                # Insert note
                cursor.execute("""
                    INSERT INTO notes 
                    (note_id, title, content, category_id, priority_id, 
                     is_completed, is_important, due_date, reminder_date, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    old_note['note_id'],
                    old_note['title'],
                    old_note['content'],
                    category_id,
                    priority_id,
                    old_note.get('is_completed', False),
                    old_note.get('is_important', False),
                    old_note.get('due_date'),
                    None,  # reminder_date (old reminder was text)
                    old_note.get('created_at'),
                    old_note.get('updated_at')
                ))
                
                # Insert attachments nếu có
                if old_note.get('attachments'):
                    try:
                        attachments = json.loads(old_note['attachments']) if isinstance(old_note['attachments'], str) else old_note['attachments']
                        if attachments and isinstance(attachments, list):
                            for file_path in attachments:
                                file_name = os.path.basename(file_path)
                                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                                file_type = os.path.splitext(file_path)[1]
                                
                                cursor.execute("""
                                    INSERT INTO attachments 
                                    (note_id, file_path, file_name, file_size, file_type)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (
                                    old_note['note_id'],
                                    file_path,
                                    file_name,
                                    file_size,
                                    file_type
                                ))
                    except:
                        pass
                
                success_count += 1
                print(f"   ✓ {old_note['title']}")
                
            except Exception as e:
                print(f"   ✗ Lỗi với note '{old_note.get('title')}': {e}")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print(f"✅ MIGRATION HOÀN TẤT!")
        print(f"   • Đã migrate: {success_count}/{len(old_notes)} ghi chú")
        print(f"   • Backup: Bảng 'notes_backup' (có thể xóa sau khi kiểm tra)")
        print("=" * 70)
        
        # 7. Hiển thị thống kê
        print("\n📊 THỐNG KÊ DATABASE MỚI:")
        cursor.execute("SELECT COUNT(*) as count FROM notes")
        print(f"   • Ghi chú: {cursor.fetchone()['count']}")
        
        cursor.execute("SELECT COUNT(*) as count FROM attachments")
        print(f"   • File đính kèm: {cursor.fetchone()['count']}")
        
        cursor.execute("SELECT COUNT(*) as count FROM categories")
        print(f"   • Danh mục: {cursor.fetchone()['count']}")
        
        cursor.execute("SELECT COUNT(*) as count FROM priorities")
        print(f"   • Mức ưu tiên: {cursor.fetchone()['count']}")
        
        print("\n💡 GỢI Ý:")
        print("   1. Kiểm tra dữ liệu trong app")
        print("   2. Nếu mọi thứ OK, xóa bảng backup:")
        print("      DROP TABLE notes_backup;")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        print("\nĐề xuất:")
        print("   • Kiểm tra MySQL đang chạy")
        print("   • Kiểm tra thông tin kết nối trong DB_CONFIG")
        print("   • Backup dữ liệu trước khi chạy migration")

if __name__ == "__main__":
    print("\n⚠️  CẢNH BÁO: Script này sẽ thay đổi cấu trúc database!")
    print("Đảm bảo bạn đã backup dữ liệu trước khi tiếp tục.\n")
    
    response = input("Tiếp tục migration? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        migrate_database()
    else:
        print("❌ Đã hủy migration.")
