"""
Model: Note (Ghi chú)
Đại diện cho một ghi chú trong hệ thống
"""

from datetime import datetime
from typing import Optional, List
import uuid


class Note:
    """Lớp ghi chú"""
    
    def __init__(
        self,
        title: str,
        content: str = "",
        category: str = "Tất cả",
        priority: str = "Thấp",
        note_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_completed: bool = False,
        due_date: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ):
        
        self.note_id = note_id
        self.title = title
        self.content = content
        self.category = category
        self.priority = priority
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.is_completed = is_completed
        self.due_date = due_date
        self.attachments = attachments or []
    
    def to_dict(self) -> dict:
        return {
            'note_id': self.note_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'is_completed': self.is_completed,
            'due_date': self.due_date,
            'attachments': self.attachments
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Note':
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
            priority=data.get('priority', 'Thấp'),
            created_at=created_at,
            updated_at=updated_at,
            is_completed=data.get('is_completed', False),
            due_date=data.get('due_date'),
            attachments=data.get('attachments', [])
        )
    
    def update(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        is_completed: Optional[bool] = None,
        due_date: Optional[str] = None
    ):
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
        if due_date is not None:
            self.due_date = due_date
        
        self.updated_at = datetime.now()
    
    def add_attachment(self, file_path: str):
        if file_path not in self.attachments:
            self.attachments.append(file_path)
            self.updated_at = datetime.now()
    
    def remove_attachment(self, file_path: str):
        if file_path in self.attachments:
            self.attachments.remove(file_path)
            self.updated_at = datetime.now()
    
    def toggle_completed(self):
        self.is_completed = not self.is_completed
        self.updated_at = datetime.now()
    
    def toggle_important(self):
        if self.priority == "Cao":
            self.priority = "Thấp"
        else:
            self.priority = "Cao"
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        """String representation for debugging"""
        status = "Completed" if self.is_completed else "Pending"
        return f"[{status}] {self.title} (Priority: {self.priority}, Category: {self.category})"
    
    def __repr__(self) -> str:
        """Debug representation"""
        return f"Note(id={self.note_id}, title='{self.title}', category='{self.category}')"
