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


class NoteController:
    """Lớp điều khiển các thao tác với ghi chú"""
    
    def __init__(self, repository: NoteRepository):
        """
        Khởi tạo controller
        
        Args:
            repository: Instance của NoteRepository
        """
        self.repository = repository
        self.current_filter = "Tất cả"
        self.current_sort = "created_at"
        self.current_sort_reverse = True  # Mới nhất trước
    
    # ==================== CRUD Operations ====================
    
    def create_note(
        self,
        title: str,
        content: str = "",
        category: str = "Tất cả",
        priority: str = "Bình thường",
        due_date: Optional[str] = None,
        is_important: bool = False
    ) -> Optional[Note]:
        """
        Tạo ghi chú mới
        
        Returns:
            Note object nếu thành công, None nếu thất bại
        """
        # Validate
        if not title or not title.strip():
            return None
        
        # Tạo note mới
        note = Note(
            title=title.strip(),
            content=content.strip(),
            category=category,
            priority=priority,
            due_date=due_date,
            is_important=is_important
        )
        
        # Lưu vào repository
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
        is_important: Optional[bool] = None,
        is_completed: Optional[bool] = None,
        reminder: Optional[str] = None
    ) -> bool:
        """Cập nhật thông tin ghi chú"""
        # Chuẩn hóa dữ liệu
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
        if is_important is not None:
            kwargs['is_important'] = is_important
        if is_completed is not None:
            kwargs['is_completed'] = is_completed
        if reminder is not None:
            kwargs['reminder'] = reminder
        
        return self.repository.update_note(note_id, **kwargs)
    
    def delete_note(self, note_id: str) -> bool:
        """
        Xóa ghi chú và các file đính kèm
        
        Returns:
            True nếu xóa thành công
        """
        note = self.repository.get_note_by_id(note_id)
        if note:
            # Xóa các file đính kèm
            for attachment in note.attachments:
                try:
                    if os.path.exists(attachment):
                        os.remove(attachment)
                except Exception as e:
                    print(f"Không thể xóa file {attachment}: {e}")
            
            # Xóa note
            return self.repository.delete_note(note_id)
        return False
    
    def get_note(self, note_id: str) -> Optional[Note]:
        """Lấy thông tin một ghi chú"""
        return self.repository.get_note_by_id(note_id)
    
    # ==================== Toggle Operations ====================
    
    def toggle_completed(self, note_id: str) -> bool:
        """Đổi trạng thái hoàn thành"""
        note = self.repository.get_note_by_id(note_id)
        if note:
            note.toggle_completed()
            # Update in database
            return self.repository.update_note(note_id, is_completed=note.is_completed)
        return False
    
    def toggle_important(self, note_id: str) -> bool:
        """Đổi trạng thái quan trọng"""
        note = self.repository.get_note_by_id(note_id)
        if note:
            note.toggle_important()
            # Update in database
            return self.repository.update_note(note_id, is_important=note.is_important)
        return False
    
    # ==================== Filter & Sort ====================
    
    def get_filtered_notes(self, filter_type: str = "Tất cả") -> List[Note]:
        """
        Lấy danh sách ghi chú theo bộ lọc
        
        Args:
            filter_type: "Tất cả", "Quan trọng", "Hoàn thành", hoặc tên category
        """
        self.current_filter = filter_type
        
        if filter_type == "Quan trọng":
            notes = self.repository.get_important_notes()
        elif filter_type == "Hoàn thành":
            notes = self.repository.get_completed_notes()
        elif filter_type == "Tất cả":
            notes = self.repository.get_all_notes()
        else:
            # Lọc theo category
            notes = self.repository.get_notes_by_category(filter_type)
        
        # Áp dụng sắp xếp
        return self.repository.sort_notes(
            notes, 
            self.current_sort, 
            self.current_sort_reverse
        )
    
    def sort_notes(self, sort_by: str, reverse: bool = False) -> List[Note]:
        """
        Sắp xếp danh sách ghi chú hiện tại
        
        Args:
            sort_by: created_at, updated_at, title, priority, due_date
            reverse: True = giảm dần
        """
        self.current_sort = sort_by
        self.current_sort_reverse = reverse
        return self.get_filtered_notes(self.current_filter)
    
    # ==================== Search ====================
    
    def search_by_keyword(self, keyword: str) -> List[Note]:
        """Tìm kiếm theo từ khóa"""
        if not keyword or not keyword.strip():
            return self.get_filtered_notes(self.current_filter)
        
        return self.repository.search_notes(keyword.strip())
    
    def search_by_date(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Note]:
        """Tìm kiếm theo ngày tạo"""
        return self.repository.search_notes_by_date_range(start_date, end_date)
    
    def get_notes_by_due_date(self, target_date: date) -> List[Note]:
        """Lấy ghi chú theo ngày đến hạn"""
        return self.repository.get_notes_by_due_date(target_date)
    
    # ==================== Attachments ====================
    
    def add_attachment(
        self, 
        note_id: str, 
        source_file: str,
        attachments_dir: str = "attachments"
    ) -> Optional[str]:
        """
        Thêm file đính kèm vào ghi chú
        
        Args:
            note_id: ID ghi chú
            source_file: Đường dẫn file gốc
            attachments_dir: Thư mục lưu file
        
        Returns:
            Đường dẫn file đã lưu, hoặc None nếu thất bại
        """
        note = self.repository.get_note_by_id(note_id)
        if not note or not os.path.exists(source_file):
            return None
        
        try:
            # Tạo thư mục nếu chưa có
            os.makedirs(attachments_dir, exist_ok=True)
            
            # Tạo tên file duy nhất
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = os.path.basename(source_file)
            name, ext = os.path.splitext(file_name)
            unique_name = f"{timestamp}_{name}{ext}"
            dest_path = os.path.join(attachments_dir, unique_name)
            
            # Copy file
            shutil.copy2(source_file, dest_path)
            
            # Thêm vào note
            note.add_attachment(dest_path)
            # Update in database
            self.repository.update_note(note_id, attachments=note.attachments)
            
            return dest_path
        except Exception as e:
            print(f"Lỗi khi thêm đính kèm: {e}")
            return None
    
    def remove_attachment(self, note_id: str, file_path: str) -> bool:
        """Xóa file đính kèm"""
        note = self.repository.get_note_by_id(note_id)
        if not note:
            return False
        
        try:
            # Xóa file vật lý
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Xóa khỏi note
            note.remove_attachment(file_path)
            # Update in database
            return self.repository.update_note(note_id, attachments=note.attachments)
        except Exception as e:
            print(f"Lỗi khi xóa đính kèm: {e}")
            return False
    
    # ==================== Categories ====================
    
    def get_categories(self) -> List[str]:
        """Lấy danh sách chủ đề"""
        categories = ["Tất cả"] + self.repository.get_categories()
        # Loại bỏ duplicate
        return list(dict.fromkeys(categories))
    
    # ==================== Statistics ====================
    
    def get_statistics(self) -> dict:
        """Lấy thống kê"""
        return self.repository.get_statistics()
    
    def get_note_count(self, filter_type: str = "Tất cả") -> int:
        """Đếm số lượng ghi chú theo bộ lọc"""
        return len(self.get_filtered_notes(filter_type))
