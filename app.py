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


class NoteApp:
    """Lớp ứng dụng chính"""
    
    def __init__(self):
        """Khởi tạo ứng dụng"""
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        
        # Initialize Model - Kết nối MySQL
        # Thay đổi thông tin kết nối tại đây nếu cần
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
        # Determine category from current filter
        category = "Tất cả"
        is_important = False
        
        if current_filter == "Quan trọng":
            is_important = True
        elif current_filter not in ["Tất cả", "Hoàn thành", "Quan trọng"]:
            category = current_filter
        
        # Create note
        note = self.controller.create_note(
            title=title,
            category=category,
            is_important=is_important
        )
        
        if note:
            # Refresh display
            self._refresh_current_view()
            # Update categories
            categories = self.controller.get_categories()
            self.view.update_categories(categories)
        else:
            messagebox.showerror("Lỗi", "Không thể tạo ghi chú!")
    
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
            messagebox.showinfo("Thành công", "Đã xóa ghi chú!")
        else:
            messagebox.showerror("Lỗi", "Không thể xóa ghi chú!")
    
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
            if file_size > 5 * 1024 * 1024:
                messagebox.showerror("Lỗi", "File quá lớn! Kích thước tối đa là 5MB.")
                return
        
        result = self.controller.add_attachment(note_id, file_path, "attachments")
        if result:
            messagebox.showinfo("Thành công", "Đã thêm file đính kèm!")
            # Refresh detail panel
            note = self.controller.get_note(note_id)
            if note:
                self.view.show_detail_panel(note)
        else:
            messagebox.showerror("Lỗi", "Không thể thêm file đính kèm!")
    
    def _handle_remove_attachment(self, note_id: str, file_path: str):
        """Xử lý xóa đính kèm"""
        success = self.controller.remove_attachment(note_id, file_path)
        if success:
            messagebox.showinfo("Thành công", "Đã xóa file đính kèm!")
            # Refresh detail panel
            note = self.controller.get_note(note_id)
            if note:
                self.view.show_detail_panel(note)
        else:
            messagebox.showerror("Lỗi", "Không thể xóa file đính kèm!")
    
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
