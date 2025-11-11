"""
Model: NoteRepository
Quản lý lưu trữ và truy xuất dữ liệu ghi chú (MySQL)
"""

import mysql.connector
from typing import List, Optional
from datetime import datetime, date
from models.Note import Note
import json


class NoteRepository:
    """Lớp quản lý lưu trữ ghi chú vào MySQL"""
    
    def __init__(self, host: str = "localhost", user: str = "root", 
                 password: str = "", database: str = "todo_app_mvc"):
        """
        Khởi tạo repository
        
        Args:
            host: MySQL host
            user: MySQL username
            password: MySQL password
            database: Tên database
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.notes: List[Note] = []
        self._create_database()
        self._create_table()
        self.load_notes()
    
    def _get_connection(self):
        """Tạo kết nối MySQL"""
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )
    
    def _create_database(self):
        """Tạo database nếu chưa tồn tại"""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Database '{self.database}' ready.")
        except Exception as e:
            print(f"Lỗi khi tạo database: {e}")
    
    def _create_table(self):
        """Tạo các bảng trong database với cấu trúc chuẩn hóa"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)  # Thêm dictionary=True
            
            # Bảng categories - Quản lý danh mục
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INT AUTO_INCREMENT PRIMARY KEY,
                    category_name VARCHAR(100) NOT NULL UNIQUE,
                    category_color VARCHAR(20),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Bảng priorities - Quản lý mức độ ưu tiên
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS priorities (
                    priority_id INT AUTO_INCREMENT PRIMARY KEY,
                    priority_name VARCHAR(50) NOT NULL UNIQUE,
                    priority_level INT NOT NULL,
                    priority_color VARCHAR(20)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Bảng notes - Bảng chính lưu ghi chú
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    note_id VARCHAR(36) PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    category_id INT,
                    priority_id INT,
                    is_completed BOOLEAN DEFAULT FALSE,
                    is_important BOOLEAN DEFAULT FALSE,
                    due_date DATE,
                    reminder_date DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
                    FOREIGN KEY (priority_id) REFERENCES priorities(priority_id) ON DELETE SET NULL,
                    INDEX idx_created_at (created_at),
                    INDEX idx_is_important (is_important),
                    INDEX idx_is_completed (is_completed),
                    INDEX idx_due_date (due_date)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Bảng attachments - Quản lý file đính kèm
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attachments (
                    attachment_id INT AUTO_INCREMENT PRIMARY KEY,
                    note_id VARCHAR(36) NOT NULL,
                    file_path TEXT NOT NULL,
                    file_name VARCHAR(255),
                    file_size BIGINT,
                    file_type VARCHAR(50),
                    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES notes(note_id) ON DELETE CASCADE,
                    INDEX idx_note_id (note_id)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Bảng tags - Quản lý thẻ tag
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    tag_id INT AUTO_INCREMENT PRIMARY KEY,
                    tag_name VARCHAR(50) NOT NULL UNIQUE,
                    tag_color VARCHAR(20),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Bảng note_tags - Quan hệ nhiều-nhiều giữa notes và tags
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS note_tags (
                    note_id VARCHAR(36) NOT NULL,
                    tag_id INT NOT NULL,
                    PRIMARY KEY (note_id, tag_id),
                    FOREIGN KEY (note_id) REFERENCES notes(note_id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Insert default categories nếu chưa có
            cursor.execute("SELECT COUNT(*) as count FROM categories")
            if cursor.fetchone()['count'] == 0:
                default_categories = [
                    ('Tất cả', '#3B82F6'),
                    ('Công việc', '#EF4444'),
                    ('Cá nhân', '#10B981'),
                    ('Học tập', '#F59E0B'),
                    ('Gia đình', '#8B5CF6'),
                    ('Sức khỏe', '#EC4899'),
                    ('Mua sắm', '#14B8A6'),
                    ('Du lịch', '#06B6D4')
                ]
                cursor.executemany(
                    "INSERT INTO categories (category_name, category_color) VALUES (%s, %s)",
                    default_categories
                )
            
            # Insert default priorities nếu chưa có
            cursor.execute("SELECT COUNT(*) as count FROM priorities")
            if cursor.fetchone()['count'] == 0:
                default_priorities = [
                    ('Bình thường', 0, '#6B7280'),
                    ('Thấp', 1, '#3B82F6'),
                    ('Trung bình', 2, '#F59E0B'),
                    ('Cao', 3, '#EF4444')
                ]
                cursor.executemany(
                    "INSERT INTO priorities (priority_name, priority_level, priority_color) VALUES (%s, %s, %s)",
                    default_priorities
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            print("Database schema ready with normalized tables.")
        except Exception as e:
            print(f"Lỗi khi tạo bảng: {e}")
    
    def load_notes(self) -> List[Note]:
        """Tải danh sách ghi chú từ MySQL với JOIN các bảng liên quan"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Query với JOIN để lấy category_name và priority_name
            cursor.execute("""
                SELECT 
                    n.*,
                    c.category_name as category,
                    p.priority_name as priority
                FROM notes n
                LEFT JOIN categories c ON n.category_id = c.category_id
                LEFT JOIN priorities p ON n.priority_id = p.priority_id
                ORDER BY n.created_at DESC
            """)
            rows = cursor.fetchall()
            
            self.notes = []
            for row in rows:
                # Lấy attachments từ bảng attachments
                cursor.execute("""
                    SELECT file_path 
                    FROM attachments 
                    WHERE note_id = %s
                    ORDER BY uploaded_at DESC
                """, (row['note_id'],))
                attachments = [att['file_path'] for att in cursor.fetchall()]
                
                note = Note(
                    note_id=row['note_id'],
                    title=row['title'],
                    content=row['content'] or '',
                    category=row['category'] or 'Cá nhân',
                    priority=row['priority'] or 'Bình thường',
                    is_completed=bool(row['is_completed']),
                    is_important=bool(row['is_important']),
                    due_date=row['due_date'].strftime('%Y-%m-%d') if row['due_date'] else None,
                    reminder=None,  # reminder_date từ DB không dùng làm string
                    attachments=attachments,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                self.notes.append(note)
            
            cursor.close()
            conn.close()
            return self.notes
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu: {e}")
            self.notes = []
            return []
    
    def add_note(self, note: Note) -> bool:
        """Thêm ghi chú mới với cấu trúc normalized"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Lấy category_id từ category_name
            cursor.execute("SELECT category_id FROM categories WHERE category_name = %s", (note.category,))
            category_row = cursor.fetchone()
            category_id = category_row['category_id'] if category_row else None
            
            # Lấy priority_id từ priority_name
            cursor.execute("SELECT priority_id FROM priorities WHERE priority_name = %s", (note.priority,))
            priority_row = cursor.fetchone()
            priority_id = priority_row['priority_id'] if priority_row else None
            
            # Insert note
            cursor.execute("""
                INSERT INTO notes 
                (note_id, title, content, category_id, priority_id, is_completed, 
                 is_important, due_date, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                note.note_id,
                note.title,
                note.content,
                category_id,
                priority_id,
                note.is_completed,
                note.is_important,
                note.due_date,
                note.created_at,
                note.updated_at
            ))
            
            # Insert attachments nếu có
            if note.attachments:
                for file_path in note.attachments:
                    import os
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    file_type = os.path.splitext(file_path)[1]
                    
                    cursor.execute("""
                        INSERT INTO attachments (note_id, file_path, file_name, file_size, file_type)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (note.note_id, file_path, file_name, file_size, file_type))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            self.notes.append(note)
            return True
        except Exception as e:
            print(f"Lỗi khi thêm ghi chú: {e}")
            return False
    
    def update_note(self, note_id: str, **kwargs) -> bool:
        """Cập nhật ghi chú theo ID với cấu trúc normalized"""
        note = self.get_note_by_id(note_id)
        if not note:
            return False
        
        try:
            # Update note object
            note.update(**kwargs)
            
            # Update database
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Lấy category_id từ category_name
            cursor.execute("SELECT category_id FROM categories WHERE category_name = %s", (note.category,))
            category_row = cursor.fetchone()
            category_id = category_row['category_id'] if category_row else None
            
            # Lấy priority_id từ priority_name
            cursor.execute("SELECT priority_id FROM priorities WHERE priority_name = %s", (note.priority,))
            priority_row = cursor.fetchone()
            priority_id = priority_row['priority_id'] if priority_row else None
            
            cursor.execute("""
                UPDATE notes 
                SET title=%s, content=%s, category_id=%s, priority_id=%s,
                    is_completed=%s, is_important=%s, due_date=%s, reminder_date=%s,
                    updated_at=%s
                WHERE note_id=%s
            """, (
                note.title,
                note.content,
                category_id,
                priority_id,
                note.is_completed,
                note.is_important,
                note.due_date,
                note.reminder,
                note.updated_at,
                note_id
            ))
            
            # Xóa attachments cũ và thêm mới
            if 'attachments' in kwargs:
                cursor.execute("DELETE FROM attachments WHERE note_id = %s", (note_id,))
                
                if note.attachments:
                    import os
                    for file_path in note.attachments:
                        file_name = os.path.basename(file_path)
                        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                        file_type = os.path.splitext(file_path)[1]
                        
                        cursor.execute("""
                            INSERT INTO attachments (note_id, file_path, file_name, file_size, file_type)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (note_id, file_path, file_name, file_size, file_type))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật ghi chú: {e}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        """Xóa ghi chú theo ID"""
        note = self.get_note_by_id(note_id)
        if not note:
            return False
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE note_id=%s", (note_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            self.notes.remove(note)
            return True
        except Exception as e:
            print(f"Lỗi khi xóa ghi chú: {e}")
            return False
    
    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """Lấy ghi chú theo ID"""
        for note in self.notes:
            if note.note_id == note_id:
                return note
        return None
    
    def get_all_notes(self) -> List[Note]:
        """Lấy tất cả ghi chú"""
        return self.notes
    
    def get_notes_by_category(self, category: str) -> List[Note]:
        """Lấy ghi chú theo chủ đề"""
        if category == "Tất cả":
            return self.notes
        return [note for note in self.notes if note.category == category]
    
    def get_important_notes(self) -> List[Note]:
        """Lấy các ghi chú quan trọng"""
        return [note for note in self.notes if note.is_important]
    
    def get_completed_notes(self) -> List[Note]:
        """Lấy các ghi chú đã hoàn thành"""
        return [note for note in self.notes if note.is_completed]
    
    def get_notes_by_due_date(self, target_date: date) -> List[Note]:
        """Lấy ghi chú theo ngày đến hạn"""
        result = []
        for note in self.notes:
            if note.due_date:
                try:
                    due = datetime.strptime(note.due_date, '%Y-%m-%d').date()
                    if due == target_date:
                        result.append(note)
                except:
                    pass
        return result
    
    def search_notes(self, keyword: str) -> List[Note]:
        """Tìm kiếm ghi chú theo từ khóa (trong tiêu đề và nội dung)"""
        keyword = keyword.lower()
        result = []
        for note in self.notes:
            if (keyword in note.title.lower() or 
                keyword in note.content.lower()):
                result.append(note)
        return result
    
    def search_notes_by_date_range(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Note]:
        """Tìm kiếm ghi chú theo khoảng ngày tạo"""
        result = []
        for note in self.notes:
            note_date = note.created_at.date() if isinstance(note.created_at, datetime) else None
            if note_date:
                if start_date and end_date:
                    if start_date <= note_date <= end_date:
                        result.append(note)
                elif start_date:
                    if note_date >= start_date:
                        result.append(note)
                elif end_date:
                    if note_date <= end_date:
                        result.append(note)
        return result
    
    def sort_notes(
        self, 
        notes: List[Note], 
        sort_by: str = "created_at", 
        reverse: bool = False
    ) -> List[Note]:
        """
        Sắp xếp danh sách ghi chú
        
        Args:
            notes: Danh sách ghi chú cần sắp xếp
            sort_by: Tiêu chí sắp xếp (created_at, updated_at, title, priority, due_date)
            reverse: True = giảm dần, False = tăng dần
        """
        if sort_by == "title":
            return sorted(notes, key=lambda n: n.title.lower(), reverse=reverse)
        elif sort_by == "priority":
            # Thứ tự: Cao > Trung bình > Thấp > Bình thường
            priority_order = {"Cao": 0, "Trung bình": 1, "Thấp": 2, "Bình thường": 3}
            return sorted(notes, key=lambda n: priority_order.get(n.priority, 3), reverse=reverse)
        elif sort_by == "updated_at":
            return sorted(notes, key=lambda n: n.updated_at, reverse=reverse)
        elif sort_by == "due_date":
            # Ghi chú có due_date lên trước
            def due_sort_key(note):
                if not note.due_date:
                    return datetime.max
                try:
                    return datetime.strptime(note.due_date, '%Y-%m-%d')
                except:
                    return datetime.max
            return sorted(notes, key=due_sort_key, reverse=reverse)
        else:  # created_at (mặc định)
            return sorted(notes, key=lambda n: n.created_at, reverse=reverse)
    
    def get_categories(self) -> List[str]:
        """Lấy danh sách các chủ đề từ bảng categories"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT category_name FROM categories ORDER BY category_name")
            categories = [row['category_name'] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return categories
        except Exception as e:
            print(f"Lỗi khi lấy danh sách categories: {e}")
            return []
    
    def get_statistics(self) -> dict:
        """Lấy thống kê về ghi chú"""
        total = len(self.notes)
        completed = len([n for n in self.notes if n.is_completed])
        important = len([n for n in self.notes if n.is_important])
        by_priority = {}
        by_category = {}
        
        for note in self.notes:
            # Đếm theo priority
            by_priority[note.priority] = by_priority.get(note.priority, 0) + 1
            # Đếm theo category
            by_category[note.category] = by_category.get(note.category, 0) + 1
        
        return {
            'total': total,
            'completed': completed,
            'pending': total - completed,
            'important': important,
            'by_priority': by_priority,
            'by_category': by_category
        }
