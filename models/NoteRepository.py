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
        
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.notes: List[Note] = []
        self._create_database()
        self._create_table()
        self.load_notes()
    
    def _get_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )
    
    def _create_database(self):
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
            print(f"Kết nối thành công database '{self.database}'.")
        except Exception as e:
            print(f"Lỗi khi tạo database: {e}")
    
    def _create_table(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INT AUTO_INCREMENT PRIMARY KEY,
                    category_name VARCHAR(100) NOT NULL UNIQUE,
                    category_color VARCHAR(20),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS priorities (
                    priority_id INT AUTO_INCREMENT PRIMARY KEY,
                    priority_name VARCHAR(50) NOT NULL UNIQUE,
                    priority_level INT NOT NULL,
                    priority_color VARCHAR(20)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INT AUTO_INCREMENT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    category_id INT,
                    priority_id INT,
                    is_completed BOOLEAN DEFAULT FALSE,
                    due_date DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
                    FOREIGN KEY (priority_id) REFERENCES priorities(priority_id) ON DELETE SET NULL,
                    INDEX idx_created_at (created_at),
                    INDEX idx_is_completed (is_completed),
                    INDEX idx_due_date (due_date)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attachments (
                    attachment_id INT AUTO_INCREMENT PRIMARY KEY,
                    note_id INT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_name VARCHAR(255),
                    file_size BIGINT,
                    file_type VARCHAR(50),
                    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES notes(note_id) ON DELETE CASCADE,
                    INDEX idx_note_id (note_id)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
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
            
            cursor.execute("SELECT COUNT(*) as count FROM priorities")
            if cursor.fetchone()['count'] == 0:
                default_priorities = [
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
        except Exception as e:
            print(f"Lỗi khi tạo bảng: {e}")
    
    def load_notes(self) -> List[Note]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    n.*,
                    c.category_name as category,
                    p.priority_name as priority
                FROM notes n
                LEFT JOIN categories c ON n.category_id = c.category_id
                LEFT JOIN priorities p ON n.priority_id = p.priority_id
                ORDER BY n.is_completed ASC, n.created_at DESC
            """)
            rows = cursor.fetchall()
            
            self.notes = []
            for row in rows:
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
                    priority=row['priority'] or 'Thấp',
                    is_completed=bool(row['is_completed']),
                    due_date=row['due_date'].strftime('%Y-%m-%d') if row['due_date'] else None,
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
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT category_id FROM categories WHERE category_name = %s", (note.category,))
            category_row = cursor.fetchone()
            category_id = category_row['category_id'] if category_row else None
            
            cursor.execute("SELECT priority_id FROM priorities WHERE priority_name = %s", (note.priority,))
            priority_row = cursor.fetchone()
            priority_id = priority_row['priority_id'] if priority_row else None
            
            cursor.execute("""
                INSERT INTO notes 
                (title, content, category_id, priority_id, is_completed, 
                 due_date, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                note.title,
                note.content,
                category_id,
                priority_id,
                note.is_completed,
                note.due_date,
                note.created_at,
                note.updated_at
            ))
            
            note_id = cursor.lastrowid
            note.note_id = note_id
            
            if note.attachments:
                for file_path in note.attachments:
                    import os
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
            
            self.notes.append(note)
            return True
        except Exception as e:
            print(f"Lỗi khi thêm ghi chú: {e}")
            return False
    
    def update_note(self, note_id: str, **kwargs) -> bool:
        note = self.get_note_by_id(note_id)
        if not note:
            return False
        
        try:
            note.update(**kwargs)
            
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT category_id FROM categories WHERE category_name = %s", (note.category,))
            category_row = cursor.fetchone()
            category_id = category_row['category_id'] if category_row else None
            
            cursor.execute("SELECT priority_id FROM priorities WHERE priority_name = %s", (note.priority,))
            priority_row = cursor.fetchone()
            priority_id = priority_row['priority_id'] if priority_row else None
            
            cursor.execute("""
                UPDATE notes 
                SET title=%s, content=%s, category_id=%s, priority_id=%s,
                    is_completed=%s, due_date=%s,
                    updated_at=%s
                WHERE note_id=%s
            """, (
                note.title,
                note.content,
                category_id,
                priority_id,
                note.is_completed,
                note.due_date,
                note.updated_at,
                note_id
            ))
            
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
        for note in self.notes:
            if note.note_id == note_id:
                return note
        return None
    
    def get_all_notes(self) -> List[Note]:
        return self.notes
    
    def get_by_category(self, category: str) -> List[Note]:
        if category == "Tất cả":
            return self.notes
        return [note for note in self.notes if note.category == category]
    
    def get_important_notes(self) -> List[Note]:
        return [note for note in self.notes if note.priority == 'Cao']
    
    def get_completed_notes(self) -> List[Note]:
        return [note for note in self.notes if note.is_completed]
    
    def get_notes_by_due_date(self, target_date: date) -> List[Note]:
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
        sort_by: str = "created_at", 
        reverse: bool = False,
        filter_type: str = None,
        category: str = None
    ) -> List[Note]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            where_conditions = []
            if filter_type == "important":
                where_conditions.append("p.priority_name = 'Cao'")
            elif filter_type == "completed":
                where_conditions.append("n.is_completed = TRUE")
            
            if category and category != "Tất cả":
                where_conditions.append(f"c.category_name = '{category}'")
            
            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
            
            order_direction = "DESC" if reverse else "ASC"
            
            if sort_by == "title":
                order_clause = f"n.title {order_direction}"
            elif sort_by == "priority":
                order_clause = f"p.priority_level {'DESC' if not reverse else 'ASC'}"
            elif sort_by == "updated_at":
                order_clause = f"n.updated_at {order_direction}"
            elif sort_by == "due_date":
                order_clause = f"n.due_date IS NULL ASC, n.due_date {order_direction}"
            else:  # created_at
                order_clause = f"n.is_completed ASC, n.created_at {order_direction}"
            
            query = f"""
                SELECT 
                    n.*,
                    c.category_name as category,
                    p.priority_name as priority
                FROM notes n
                LEFT JOIN categories c ON n.category_id = c.category_id
                LEFT JOIN priorities p ON n.priority_id = p.priority_id
                {where_clause}
                ORDER BY {order_clause}
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            sorted_notes = []
            for row in rows:
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
                    priority=row['priority'] or 'Thấp',
                    is_completed=bool(row['is_completed']),
                    due_date=row['due_date'].strftime('%Y-%m-%d') if row['due_date'] else None,
                    attachments=attachments,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                sorted_notes.append(note)
            
            cursor.close()
            conn.close()
            
            self.notes = sorted_notes
            return sorted_notes
            
        except Exception as e:
            print(f"Lỗi khi sắp xếp ghi chú: {e}")
            return self.notes
    
    def get_categories(self) -> List[str]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT category_name FROM categories")
            categories = [row['category_name'] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return categories
        except Exception as e:
            print(f"Lỗi khi lấy danh sách categories: {e}")
            return []
    
    def add_category(self, category_name: str, category_color: str = "#3B82F6") -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categories (category_name, category_color) VALUES (%s, %s)",
                (category_name, category_color)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except mysql.connector.IntegrityError:
            print(f"Danh mục '{category_name}' đã tồn tại")
            return False
        except Exception as e:
            print(f"Lỗi khi thêm danh mục: {e}")
            return False
    
    def update_category(self, old_name: str, new_name: str) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categories SET category_name = %s WHERE category_name = %s",
                (new_name, old_name)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật danh mục: {e}")
            return False
    
    def delete_category(self, category_name: str) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM categories WHERE category_name = %s",
                (category_name,)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Lỗi khi xóa danh mục: {e}")
            return False
    
    def get_statistics(self) -> dict:
        total = len(self.notes)
        completed = len([n for n in self.notes if n.is_completed])
        important = len([n for n in self.notes if n.priority == 'Cao'])
        by_priority = {}
        by_category = {}
        
        for note in self.notes:
            by_priority[note.priority] = by_priority.get(note.priority, 0) + 1
            by_category[note.category] = by_category.get(note.category, 0) + 1
        
        return {
            'total': total,
            'completed': completed,
            'pending': total - completed,
            'important': important,
            'by_priority': by_priority,
            'by_category': by_category
        }
