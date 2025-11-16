"""
Controller: NoteController
Điều khiển logic nghiệp vụ và kết nối Model-View
"""

from typing import List, Optional
from datetime import datetime, date
from models.Note import Note
from models.NoteRepository import NoteRepository
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import FilterType, Priority


class NoteController:
    """Lớp điều khiển các thao tác với ghi chú"""
    
    def __init__(self, repository: NoteRepository):
        self.repository = repository
        self.current_filter = FilterType.ALL
        self.current_sort = "created_at"
        self.current_sort_reverse = True
    
    # ==================== CRUD Operations ====================
    
    def create_note(
        self,
        title: str,
        content: str = "",
        category: str = None,
        priority: str = None,
        due_date: Optional[str] = None
    ) -> Optional[Note]:
        
        if not title or not title.strip():
            return None
        
        if category is None:
            category = FilterType.ALL
        if priority is None:
            priority = Priority.LOW
        
        note = Note(
            title=title.strip(),
            content=content.strip(),
            category=category,
            priority=priority,
            due_date=due_date
        )
        
        if self.repository.add_note(note):
            return note
        return None
    
    def update_note(
        self,
        note_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        is_completed: Optional[bool] = None
    ) -> bool:
        
        kwargs = {}
        if title is not None and title.strip():
            kwargs['title'] = title.strip()
        if content is not None:
            kwargs['content'] = content.strip()
        if category is not None:
            kwargs['category'] = category
        if priority is not None:
            kwargs['priority'] = priority
        if due_date is not None:
            kwargs['due_date'] = due_date
        if is_completed is not None:
            kwargs['is_completed'] = is_completed
        
        return self.repository.update_note(note_id, **kwargs)
    
    def delete_note(self, note_id: str) -> bool:
        note = self.repository.get_note_by_id(note_id)
        if note:
            for attachment in note.attachments:
                try:
                    if os.path.exists(attachment):
                        os.remove(attachment)
                except Exception as e:
                    print(f"Không thể xóa file {attachment}: {e}")
            return self.repository.delete_note(note_id)
        return False
    
    def get_note(self, note_id: str) -> Optional[Note]:
        """Lấy thông tin một ghi chú"""
        return self.repository.get_note_by_id(note_id)
    
    # ==================== Toggle Operations ====================
    
    def toggle_completed(self, note_id: str) -> bool:
        note = self.repository.get_note_by_id(note_id)
        if note:
            note.toggle_completed()
            return self.repository.update_note(note_id, is_completed=note.is_completed)
        return False
    
    def toggle_important(self, note_id: str) -> bool:
        note = self.repository.get_note_by_id(note_id)
        if note:
            note.toggle_important()
            return self.repository.update_note(note_id, priority=note.priority)
        return False
    
    # ==================== Filter & Sort ====================
    
    def get_filtered_notes(self, filter_type: str = None) -> List[Note]:
        if filter_type is None:
            filter_type = FilterType.ALL
            
        self.current_filter = filter_type
        
        # Xác định filter_type và category cho query
        query_filter_type = None
        query_category = None
        
        if filter_type == FilterType.IMPORTANT:
            query_filter_type = "important"
        elif filter_type == FilterType.COMPLETED:
            query_filter_type = "completed"
        elif filter_type != FilterType.ALL:
            query_category = filter_type
        
        # Query DB với filter và sort
        return self.repository.sort_notes(
            self.current_sort,
            self.current_sort_reverse,
            filter_type=query_filter_type,
            category=query_category
        )
    
    def sort_notes(self, sort_by: str, reverse: bool = False) -> List[Note]:
        self.current_sort = sort_by
        self.current_sort_reverse = reverse
        return self.get_filtered_notes(self.current_filter)
    
    # ==================== Search ====================
    
    def search_by_keyword(self, keyword: str) -> List[Note]:
        if not keyword or not keyword.strip():
            return self.get_filtered_notes(self.current_filter)
        
        return self.repository.search_notes(keyword.strip())
    
    def search_by_date(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Note]:
        return self.repository.search_notes_by_date_range(start_date, end_date)
    
    def get_notes_by_due_date(self, target_date: date) -> List[Note]:
        return self.repository.get_notes_by_due_date(target_date)
    
    # ==================== Attachments ====================
    
    def add_attachment(
        self, 
        note_id: str, 
        source_file: str,
        attachments_dir: str = "attachments"
    ) -> Optional[str]:
        
        note = self.repository.get_note_by_id(note_id)
        if not note or not os.path.exists(source_file):
            return None
        
        try:
            os.makedirs(attachments_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = os.path.basename(source_file)
            name, ext = os.path.splitext(file_name)
            unique_name = f"{timestamp}_{name}{ext}"
            dest_path = os.path.join(attachments_dir, unique_name)
            
            shutil.copy2(source_file, dest_path)
            
            note.add_attachment(dest_path)
            self.repository.update_note(note_id, attachments=note.attachments)
            
            return dest_path
        except Exception as e:
            print(f"Lỗi khi thêm đính kèm: {e}")
            return None
    
    def remove_attachment(self, note_id: str, file_path: str) -> bool:
        note = self.repository.get_note_by_id(note_id)
        if not note:
            return False
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            note.remove_attachment(file_path)
            return self.repository.update_note(note_id, attachments=note.attachments)
        except Exception as e:
            print(f"Lỗi khi xóa đính kèm: {e}")
            return False
    
    # ==================== Categories ====================
    
    def get_categories(self) -> List[str]:
        categories = [FilterType.ALL] + self.repository.get_categories()
        return list(dict.fromkeys(categories))
    
    def add_category(self, category_name: str, category_color: str = "#3B82F6") -> bool:
        if not category_name or not category_name.strip():
            return False
        return self.repository.add_category(category_name.strip(), category_color)
    
    def update_category(self, old_name: str, new_name: str) -> bool:
        if not new_name or not new_name.strip():
            return False
        return self.repository.update_category(old_name, new_name.strip())
    
    def delete_category(self, category_name: str) -> bool:
        # Không cho xóa các danh mục đặc biệt
        protected = [FilterType.ALL, FilterType.IMPORTANT, FilterType.COMPLETED]
        if category_name in protected:
            return False
        return self.repository.delete_category(category_name)
    
    # ==================== Statistics ====================
    
    def get_statistics(self) -> dict:
        return self.repository.get_statistics()
    
    def get_note_count(self, filter_type: str = "Tất cả") -> int:
        return len(self.get_filtered_notes(filter_type))
