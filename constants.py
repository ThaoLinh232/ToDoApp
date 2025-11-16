"""
Constants and Enums
Định nghĩa các hằng số và enums để tránh magic strings
"""

from enum import Enum


# ==================== Filter Types ======================================

class FilterType:
    """Các loại bộ lọc"""
    ALL = "Tất cả"
    IMPORTANT = "Quan trọng"
    COMPLETED = "Hoàn thành"


# ==================== Priorities ====================

class Priority:
    """Mức độ ưu tiên"""
    LOW = "Thấp"
    MEDIUM = "Trung bình"
    HIGH = "Cao"
    
    @classmethod
    def all(cls):
        return [cls.LOW, cls.MEDIUM, cls.HIGH]


# ==================== Colors ====================

class Colors:
    """Màu sắc theme"""
    ACCENT = '#3B82F6'
    ACCENT_HOVER = '#60A5FA'
    SUCCESS = '#10B981'
    DANGER = '#EF4444'
    WARNING = '#F59E0B'
    STAR = '#FBBF24'
    
    # Priority colors
    PRIORITY_HIGH = '#EF4444'
    PRIORITY_MEDIUM = '#F59E0B'
    PRIORITY_LOW = '#3B82F6'
    
    @classmethod
    def get_priority_color(cls, priority: str):
        color_map = {
            Priority.HIGH: cls.PRIORITY_HIGH,
            Priority.MEDIUM: cls.PRIORITY_MEDIUM,
            Priority.LOW: cls.PRIORITY_LOW
        }
        return color_map.get(priority, cls.PRIORITY_LOW)


# ==================== Sort Options ====================

class SortOption:
    """Các tùy chọn sắp xếp"""
    NEWEST = "Mới nhất"
    OLDEST = "Cũ nhất"
    TITLE_ASC = "Tên A-Z"
    TITLE_DESC = "Tên Z-A"
    PRIORITY_HIGH = "Ưu tiên cao"
    DUE_DATE = "Ngày đến hạn"
    
    @classmethod
    def all(cls):
        return [
            cls.NEWEST,
            cls.OLDEST,
            cls.TITLE_ASC,
            cls.TITLE_DESC,
            cls.PRIORITY_HIGH,
            cls.DUE_DATE
        ]
    
    @classmethod
    def get_mapping(cls):
        """Mapping từ display name sang (field, reverse)"""
        return {
            cls.NEWEST: ("created_at", True),
            cls.OLDEST: ("created_at", False),
            cls.TITLE_ASC: ("title", False),
            cls.TITLE_DESC: ("title", True),
            cls.PRIORITY_HIGH: ("priority", False),
            cls.DUE_DATE: ("due_date", False)
        }


# ==================== File Constraints ====================

class FileConstraints:
    """Giới hạn cho file đính kèm"""
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    ATTACHMENTS_DIR = "attachments"


# ==================== UI Constants ====================

class UIConstants:
    """Hằng số UI"""
    # Window
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    
    # Sidebar
    SIDEBAR_WIDTH = 250


# ==================== Messages ====================

class Messages:
    """Thông báo cho người dùng"""
    # Success
    NOTE_CREATED = "Đã tạo ghi chú mới!"
    NOTE_UPDATED = "Đã lưu thay đổi!"
    NOTE_DELETED = "Đã xóa ghi chú!"
    ATTACHMENT_ADDED = "Đã thêm file đính kèm!"
    ATTACHMENT_REMOVED = "Đã xóa file đính kèm!"
    
    # Error
    ERROR_CREATE_NOTE = "Không thể tạo ghi chú!"
    ERROR_UPDATE_NOTE = "Không thể lưu thay đổi!"
    ERROR_DELETE_NOTE = "Không thể xóa ghi chú!"
    ERROR_ADD_ATTACHMENT = "Không thể thêm file đính kèm!"
    ERROR_REMOVE_ATTACHMENT = "Không thể xóa file đính kèm!"
    ERROR_TITLE_EMPTY = "Tiêu đề không được để trống!"
    ERROR_FILE_TOO_LARGE = "File quá lớn! Kích thước tối đa là 5MB."
    ERROR_NO_IMAGE = "File không phải hình ảnh hợp lệ!"
    
    # Warning
    WARN_TITLE_REQUIRED = "Vui lòng nhập tiêu đề ghi chú!"
    WARN_CONFIRM_DELETE = "Bạn có chắc chắn muốn xóa ghi chú này?\nThao tác này không thể hoàn tác!"
    WARN_CONFIRM_DELETE_ATTACHMENT = "Bạn có chắc chắn muốn xóa file đính kèm này?"
    
    # Info
    INFO_NO_NOTES = "Chưa có ghi chú nào"
    INFO_SEARCH_RESULTS = "Tìm thấy {} ghi chú"
