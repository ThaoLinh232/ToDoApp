"""
Model: Note (Ghi chú)
Đại diện cho một ghi chú trong hệ thống
"""

from datetime import datetime
from typing import Optional, List
import uuid


class Note:
    """Lớp đại diện cho một ghi chú"""
    
    def __init__(
        self,
        title: str,
        content: str = "",
        category: str = "Tất cả",
        priority: str = "Bình thường",
        note_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_completed: bool = False,
        is_important: bool = False,
        due_date: Optional[str] = None,
        reminder: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ):
        """
        Khởi tạo ghi chú mới
        
        Args:
            title: Tiêu đề ghi chú (bắt buộc)
            content: Nội dung chi tiết
            category: Chủ đề/danh mục (Công việc, Cá nhân, Học tập, v.v.)
            priority: Mức độ ưu tiên (Cao, Trung bình, Thấp, Bình thường)
            note_id: ID duy nhất (tự động tạo nếu không có)
            created_at: Thời gian tạo
            updated_at: Thời gian cập nhật
            is_completed: Trạng thái hoàn thành
            is_important: Đánh dấu quan trọng
            due_date: Ngày đến hạn (YYYY-MM-DD)
            reminder: Thời gian nhắc nhở
            attachments: Danh sách đường dẫn file đính kèm
        """
        self.note_id = note_id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.category = category
        self.priority = priority
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.is_completed = is_completed
        self.is_important = is_important
        self.due_date = due_date
        self.reminder = reminder
        self.attachments = attachments or []
    
    def to_dict(self) -> dict:
        """Chuyển đổi Note thành dictionary để lưu JSON"""
        return {
            'note_id': self.note_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'is_completed': self.is_completed,
            'is_important': self.is_important,
            'due_date': self.due_date,
            'reminder': self.reminder,
            'attachments': self.attachments
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Note':
        """Tạo Note từ dictionary (load từ JSON)"""
        # Chuyển đổi string thành datetime
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            note_id=data.get('note_id'),
            title=data.get('title', ''),
            content=data.get('content', ''),
            category=data.get('category', 'Tất cả'),
            priority=data.get('priority', 'Bình thường'),
            created_at=created_at,
            updated_at=updated_at,
            is_completed=data.get('is_completed', False),
            is_important=data.get('is_important', False),
            due_date=data.get('due_date'),
            reminder=data.get('reminder'),
            attachments=data.get('attachments', [])
        )
    
    def update(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        is_completed: Optional[bool] = None,
        is_important: Optional[bool] = None,
        due_date: Optional[str] = None,
        reminder: Optional[str] = None
    ):
        """Cập nhật thông tin ghi chú"""
        if title is not None:
            self.title = title
        if content is not None:
            self.content = content
        if category is not None:
            self.category = category
        if priority is not None:
            self.priority = priority
        if is_completed is not None:
            self.is_completed = is_completed
        if is_important is not None:
            self.is_important = is_important
        if due_date is not None:
            self.due_date = due_date
        if reminder is not None:
            self.reminder = reminder
        
        self.updated_at = datetime.now()
    
    def add_attachment(self, file_path: str):
        """Thêm file đính kèm"""
        if file_path not in self.attachments:
            self.attachments.append(file_path)
            self.updated_at = datetime.now()
    
    def remove_attachment(self, file_path: str):
        """Xóa file đính kèm"""
        if file_path in self.attachments:
            self.attachments.remove(file_path)
            self.updated_at = datetime.now()
    
    def toggle_completed(self):
        """Đổi trạng thái hoàn thành"""
        self.is_completed = not self.is_completed
        self.updated_at = datetime.now()
    
    def toggle_important(self):
        """Đổi trạng thái quan trọng"""
        self.is_important = not self.is_important
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        """String representation"""
        status = "✓" if self.is_completed else "○"
        star = "⭐" if self.is_important else ""
        return f"{status} {self.title} [{self.priority}] {star}"
    
    def __repr__(self) -> str:
        """Debug representation"""
        return f"Note(id={self.note_id[:8]}, title='{self.title}', category='{self.category}')"
