"""
Main Application
Kết nối Model-View-Controller và khởi động ứng dụng
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Note, NoteRepository
from controllers import NoteController
from views import MainView
from constants import FilterType, Messages, FileConstraints, Priority


class NoteApp:
    """Lớp ứng dụng chính"""
    
    def __init__(self):
        """Khởi tạo ứng dụng"""
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        
        # Kết nối MySQL
        self.repository = NoteRepository(
            host="localhost",
            user="root",
            password="",
            database="todo_app_mvc"
        )
        
        # Initialize Controller
        self.controller = NoteController(self.repository)
        
        # Initialize View
        self.view = MainView(self.root)
        
        # Connect callbacks
        self._setup_callbacks()
        
        # Load initial data
        self._load_initial_data()
    
    def _setup_callbacks(self):
        """Kết nối các callback từ View đến Controller"""
        # CRUD operations
        self.view.on_add_note = self._handle_add_note
        self.view.on_update_note = self._handle_update_note
        self.view.on_delete_note = self._handle_delete_note
        
        # Toggle operations
        self.view.on_toggle_completed = self._handle_toggle_completed
        self.view.on_toggle_important = self._handle_toggle_important
        
        # Filter and sort
        self.view.on_filter_change = self._handle_filter_change
        self.view.on_sort_change = self._handle_sort_change
        self.view.on_search = self._handle_search
        
        # Attachments
        self.view.on_add_attachment = self._handle_add_attachment
        self.view.on_remove_attachment = self._handle_remove_attachment
        
        # Categories
        self.view.on_add_category = self._handle_add_category
        self.view.on_edit_category = self._handle_edit_category
        self.view.on_delete_category = self._handle_delete_category
    
    def _load_initial_data(self):
        """Tải dữ liệu ban đầu"""
        # Load all notes
        notes = self.controller.get_filtered_notes("Tất cả")
        self.view.display_notes(notes)
        
        # Update categories
        categories = self.controller.get_categories()
        self.view.update_categories(categories)
    
    # ==================== CRUD Handlers ====================
    
    def _handle_add_note(self, title: str, current_filter: str):
        """Xử lý thêm ghi chú mới"""
        category = FilterType.ALL
        priority = Priority.LOW
        
        if current_filter == FilterType.IMPORTANT:
            priority = Priority.HIGH
        elif current_filter not in [FilterType.ALL, FilterType.COMPLETED, FilterType.IMPORTANT]:
            category = current_filter
        
        # Create note
        note = self.controller.create_note(
            title=title,
            category=category,
            priority=priority
        )
        
        if note:
            self._refresh_current_view()
            categories = self.controller.get_categories()
            self.view.update_categories(categories)
        else:
            messagebox.showerror("Lỗi", Messages.ERROR_CREATE_NOTE)
    
    def _handle_update_note(self, note_id: str, **kwargs):
        """Xử lý cập nhật ghi chú"""
        success = self.controller.update_note(note_id, **kwargs)
        if success:
            self._refresh_current_view()
            # Update categories if changed
            categories = self.controller.get_categories()
            self.view.update_categories(categories)
            # Refresh detail panel if open
            note = self.controller.get_note(note_id)
            if note and self.view.selected_note_id == note_id:
                self.view.show_detail_panel(note)
        return success
    
    def _handle_delete_note(self, note_id: str):
        """Xử lý xóa ghi chú"""
        success = self.controller.delete_note(note_id)
        if success:
            self._refresh_current_view()
            messagebox.showinfo("Thành công", Messages.NOTE_DELETED)
        else:
            messagebox.showerror("Lỗi", Messages.ERROR_DELETE_NOTE)
    
    # ==================== Toggle Handlers ====================
    
    def _handle_toggle_completed(self, note_id: str):
        """Xử lý toggle hoàn thành"""
        self.controller.toggle_completed(note_id)
        self._refresh_current_view()
        
        # Update detail panel if open
        if self.view.selected_note_id == note_id:
            note = self.controller.get_note(note_id)
            if note:
                self.view.show_detail_panel(note)
    
    def _handle_toggle_important(self, note_id: str):
        """Xử lý toggle quan trọng"""
        self.controller.toggle_important(note_id)
        self._refresh_current_view()
        
        # Update detail panel if open
        if self.view.selected_note_id == note_id:
            note = self.controller.get_note(note_id)
            if note:
                self.view.show_detail_panel(note)
    
    # ==================== Filter & Sort Handlers ====================
    
    def _handle_filter_change(self, filter_type: str):
        """Xử lý thay đổi bộ lọc"""
        notes = self.controller.get_filtered_notes(filter_type)
        self.view.display_notes(notes)
    
    def _handle_sort_change(self, sort_by: str, reverse: bool):
        """Xử lý thay đổi sắp xếp"""
        notes = self.controller.sort_notes(sort_by, reverse)
        self.view.display_notes(notes)
    
    def _handle_search(self, keyword: str):
        """Xử lý tìm kiếm"""
        if keyword:
            notes = self.controller.search_by_keyword(keyword)
        else:
            notes = self.controller.get_filtered_notes(self.view.current_filter)
        self.view.display_notes(notes)
    
    # ==================== Attachment Handlers ====================
    
    def _handle_add_attachment(self, note_id: str, file_path: str):
        """Xử lý thêm đính kèm"""
        # Check file size (max 5MB)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > FileConstraints.MAX_FILE_SIZE:
                messagebox.showerror("Lỗi", Messages.ERROR_FILE_TOO_LARGE)
                return
        
        result = self.controller.add_attachment(note_id, file_path, FileConstraints.ATTACHMENTS_DIR)
        if result:
            messagebox.showinfo("Thành công", Messages.ATTACHMENT_ADDED)
            # Refresh detail panel
            note = self.controller.get_note(note_id)
            if note:
                self.view.show_detail_panel(note)
        else:
            messagebox.showerror("Lỗi", Messages.ERROR_ADD_ATTACHMENT)
    
    def _handle_remove_attachment(self, note_id: str, file_path: str):
        """Xử lý xóa đính kèm"""
        success = self.controller.remove_attachment(note_id, file_path)
        if success:
            messagebox.showinfo("Thành công", Messages.ATTACHMENT_REMOVED)
            # Refresh detail panel
            note = self.controller.get_note(note_id)
            if note:
                self.view.show_detail_panel(note)
        else:
            messagebox.showerror("Lỗi", Messages.ERROR_REMOVE_ATTACHMENT)
    
    def _handle_add_category(self, category_name: str) -> bool:
        """Xử lý thêm danh mục mới"""
        import random
        # Generate random color
        colors = ["#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6", "#F97316"]
        color = random.choice(colors)
        
        success = self.controller.add_category(category_name, color)
        if success:
            messagebox.showinfo("Thành công", f"Đã thêm danh mục '{category_name}'")
            categories = self.controller.get_categories()
            self.view.update_categories(categories)
            return True
        else:
            messagebox.showerror("Lỗi", f"Không thể thêm danh mục '{category_name}'. Có thể đã tồn tại.")
            return False
    
    def _handle_edit_category(self, old_name: str, new_name: str) -> bool:
        """Xử lý sửa tên danh mục"""
        success = self.controller.update_category(old_name, new_name)
        if success:
            messagebox.showinfo("Thành công", f"Đã đổi tên danh mục '{old_name}' thành '{new_name}'")
            
            # Reload all
            self.controller.repository.load_notes()
            
            # Refresh categories
            categories = self.controller.get_categories()
            self.view.update_categories(categories)
            
            # Tự động click vào danh mục mới để reload giao diện
            self.view.select_category(new_name)
            
            return True
        else:
            messagebox.showerror("Lỗi", f"Không thể đổi tên danh mục '{old_name}'.")
            return False
    
    def _handle_delete_category(self, category_name: str) -> bool:
        """Xử lý xóa danh mục"""
        from tkinter import messagebox as mb
        confirm = mb.askyesno("Xác nhận", f"Bạn có chắc muốn xóa danh mục '{category_name}'?\nCác ghi chú trong danh mục này sẽ không bị xóa.")
        if not confirm:
            return False
        
        success = self.controller.delete_category(category_name)
        if success:
            messagebox.showinfo("Thành công", f"Đã xóa danh mục '{category_name}'")
            
            # Reload all notes from database
            self.controller.repository.load_notes()
            
            # Refresh categories
            categories = self.controller.get_categories()
            self.view.update_categories(categories)
            
            # Switch to "Tất cả"
            self._handle_filter_change(FilterType.ALL)
            return True
        else:
            messagebox.showerror("Lỗi", f"Không thể xóa danh mục '{category_name}'.")
            return False
    
    # ==================== Helper Methods ====================
    
    def _refresh_current_view(self):
        """Refresh view hiện tại"""
        notes = self.controller.get_filtered_notes(self.view.current_filter)
        self.view.display_notes(notes)
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()


def main():
    """Entry point"""
    try:
        app = NoteApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Lỗi nghiêm trọng", f"Ứng dụng gặp lỗi: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
