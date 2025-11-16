"""
View: MainView
Giao diện chính của ứng dụng (Microsoft To Do style)
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date, timedelta
from typing import Optional, Callable, List
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import os
import sys

# Import constants
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    FilterType, Priority, Colors, SortOption,
    FileConstraints, UIConstants, Messages
)


class MainView:
    """Lớp giao diện chính"""
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("To-do App")
        self.root.geometry(f"{UIConstants.WINDOW_WIDTH}x{UIConstants.WINDOW_HEIGHT}")
        
        self.on_add_note: Optional[Callable] = None
        self.on_update_note: Optional[Callable] = None
        self.on_delete_note: Optional[Callable] = None
        self.on_toggle_completed: Optional[Callable] = None
        self.on_toggle_important: Optional[Callable] = None
        self.on_filter_change: Optional[Callable] = None
        self.on_sort_change: Optional[Callable] = None
        self.on_search: Optional[Callable] = None
        self.on_add_attachment: Optional[Callable] = None
        self.on_remove_attachment: Optional[Callable] = None
        self.on_add_category: Optional[Callable] = None
        self.on_edit_category: Optional[Callable] = None
        self.on_delete_category: Optional[Callable] = None
        
        self.selected_note_id: Optional[str] = None
        self.current_filter = FilterType.ALL
        self.available_categories: List[str] = []
        
        self._load_icons()
        
        self.colors = {
            'accent': Colors.ACCENT,
            'accent_hover': Colors.ACCENT_HOVER,
            'success': Colors.SUCCESS,
            'danger': Colors.DANGER,
            'warning': Colors.WARNING,
            'star': Colors.STAR,
            'priority_high': Colors.PRIORITY_HIGH,
            'priority_medium': Colors.PRIORITY_MEDIUM,
            'priority_low': Colors.PRIORITY_LOW,
        }
        
        self._setup_ui()
    
    def _load_icons(self):
        try:
            icons_dir = os.path.join(os.path.dirname(__file__), "..", "icons")
            
            # Star icons
            star_path = os.path.join(icons_dir, "star.png")
            star_blank_path = os.path.join(icons_dir, "star_blank.png")
            
            if os.path.exists(star_path):
                star_img = Image.open(star_path)
                star_img = star_img.resize((20, 20), Image.Resampling.LANCZOS)
                self.star_icon = ctk.CTkImage(light_image=star_img, dark_image=star_img, size=(20, 20))
            else:
                self.star_icon = None
            
            if os.path.exists(star_blank_path):
                star_blank_img = Image.open(star_blank_path)
                star_blank_img = star_blank_img.resize((20, 20), Image.Resampling.LANCZOS)
                self.star_blank_icon = ctk.CTkImage(light_image=star_blank_img, dark_image=star_blank_img, size=(20, 20))
            else:
                self.star_blank_icon = None
            
            category_path = os.path.join(icons_dir, "category-list.png")
            if os.path.exists(category_path):
                category_img = Image.open(category_path)
                category_img = category_img.resize((18, 18), Image.Resampling.LANCZOS)
                self.category_icon = ctk.CTkImage(light_image=category_img, dark_image=category_img, size=(18, 18))
            else:
                self.category_icon = None
            
            check_path = os.path.join(icons_dir, "check.png")
            if os.path.exists(check_path):
                check_img = Image.open(check_path)
                check_img = check_img.resize((16, 16), Image.Resampling.LANCZOS)
                self.check_icon = ctk.CTkImage(light_image=check_img, dark_image=check_img, size=(16, 16))
            else:
                self.check_icon = None
            
            calendar_path = os.path.join(icons_dir, "calendar.png")
            if os.path.exists(calendar_path):
                calendar_img = Image.open(calendar_path)
                calendar_img = calendar_img.resize((16, 16), Image.Resampling.LANCZOS)
                self.calendar_icon = ctk.CTkImage(light_image=calendar_img, dark_image=calendar_img, size=(16, 16))
            else:
                self.calendar_icon = None
            
            attachment_path = os.path.join(icons_dir, "attachment.png")
            if os.path.exists(attachment_path):
                attachment_img = Image.open(attachment_path)
                attachment_img = attachment_img.resize((16, 16), Image.Resampling.LANCZOS)
                self.attachment_icon = ctk.CTkImage(light_image=attachment_img, dark_image=attachment_img, size=(16, 16))
            else:
                self.attachment_icon = None
            
            add_path = os.path.join(icons_dir, "add.png")
            if os.path.exists(add_path):
                add_img = Image.open(add_path)
                add_img = add_img.resize((16, 16), Image.Resampling.LANCZOS)
                self.add_icon = ctk.CTkImage(light_image=add_img, dark_image=add_img, size=(16, 16))
            else:
                self.add_icon = None
            
            delete_path = os.path.join(icons_dir, "delete.png")
            if os.path.exists(delete_path):
                delete_img = Image.open(delete_path)
                delete_img = delete_img.resize((16, 16), Image.Resampling.LANCZOS)
                self.delete_icon = ctk.CTkImage(light_image=delete_img, dark_image=delete_img, size=(16, 16))
            else:
                self.delete_icon = None
            
            search_path = os.path.join(icons_dir, "search.png")
            if os.path.exists(search_path):
                search_img = Image.open(search_path)
                search_img = search_img.resize((16, 16), Image.Resampling.LANCZOS)
                self.search_icon = ctk.CTkImage(light_image=search_img, dark_image=search_img, size=(16, 16))
            else:
                self.search_icon = None
            
            save_path = os.path.join(icons_dir, "save.png")
            if os.path.exists(save_path):
                save_img = Image.open(save_path)
                save_img = save_img.resize((16, 16), Image.Resampling.LANCZOS)
                self.save_icon = ctk.CTkImage(light_image=save_img, dark_image=save_img, size=(16, 16))
            else:
                self.save_icon = None
            
            file_path = os.path.join(icons_dir, "file.png")
            if os.path.exists(file_path):
                file_img = Image.open(file_path)
                file_img = file_img.resize((18, 18), Image.Resampling.LANCZOS)
                self.file_icon = ctk.CTkImage(light_image=file_img, dark_image=file_img, size=(18, 18))
            else:
                self.file_icon = None
                
        except Exception as e:
            print(f"Lỗi khi load icons: {e}")
            self.star_icon = None
            self.star_blank_icon = None
            self.category_icon = None
            self.check_icon = None
            self.calendar_icon = None
            self.attachment_icon = None
            self.add_icon = None
            self.delete_icon = None
            self.search_icon = None
            self.save_icon = None
            self.file_icon = None
    
    def _setup_ui(self):
        # Configure grid - column 0: sidebar trái, column 1: main content, column 2: detail panel phải
        self.root.grid_columnconfigure(0, weight=0, minsize=UIConstants.SIDEBAR_WIDTH)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=0)
        self.root.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_main_content()
        self._create_detail_panel()
    
    # ==================== Sidebar ====================
    
    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, width=UIConstants.SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="To-do App",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(30, 20), padx=20)
        
        views_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        views_frame.pack(fill="x", padx=10, pady=10)
        
        if self.file_icon:
            all_btn = ctk.CTkButton(
                views_frame,
                text=f" {FilterType.ALL}",
                image=self.file_icon,
                compound="left",
                font=ctk.CTkFont(size=14),
                height=45,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=lambda: self._on_filter_click(FilterType.ALL)
            )
            all_btn.pack(fill="x", pady=2)
        else:
            self._create_sidebar_button(
                views_frame, 
                f"{FilterType.ALL}", 
                lambda: self._on_filter_click(FilterType.ALL)
            )
        # Important filter với star icon
        if self.star_icon:
            important_btn = ctk.CTkButton(
                views_frame,
                text=f" {FilterType.IMPORTANT}",
                image=self.star_icon,
                compound="left",
                font=ctk.CTkFont(size=14),
                height=45,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=lambda: self._on_filter_click(FilterType.IMPORTANT)
            )
            important_btn.pack(fill="x", pady=2)
        else:
            self._create_sidebar_button(
                views_frame, 
                f"{FilterType.IMPORTANT}", 
                lambda: self._on_filter_click(FilterType.IMPORTANT)
            )
        # Completed filter với check icon
        if self.check_icon:
            completed_btn = ctk.CTkButton(
                views_frame,
                text=f" {FilterType.COMPLETED}",
                image=self.check_icon,
                compound="left",
                font=ctk.CTkFont(size=14),
                height=45,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=lambda: self._on_filter_click(FilterType.COMPLETED)
            )
            completed_btn.pack(fill="x", pady=2)
        else:
            self._create_sidebar_button(
                views_frame, 
                f"{FilterType.COMPLETED}", 
                lambda: self._on_filter_click(FilterType.COMPLETED)
            )
        
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", padx=20, pady=15)
        
        # Categories section
        categories_label = ctk.CTkLabel(
            self.sidebar,
            text="Danh mục",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        categories_label.pack(fill="x", padx=20, pady=(10, 5))
        
        # Categories list
        self.categories_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent"
        )
        self.categories_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Add Category
        if self.add_icon:
            self.add_category_btn = ctk.CTkButton(
                self.sidebar,
                text=" Thêm danh mục",
                image=self.add_icon,
                compound="left",
                command=self._on_add_category_click,
                height=35,
                corner_radius=8,
                fg_color=("#e0e0e0", "#2b2b2b"),
                hover_color=("#d0d0d0", "#3b3b3b"),
                text_color=("#000000", "#ffffff")
            )
        else:
            self.add_category_btn = ctk.CTkButton(
                self.sidebar,
                text="Thêm danh mục",
                command=self._on_add_category_click,
                height=35,
                corner_radius=8,
                fg_color=("#e0e0e0", "#2b2b2b"),
                hover_color=("#d0d0d0", "#3b3b3b"),
                text_color=("#000000", "#ffffff")
            )
        self.add_category_btn.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # Category buttons
        self.category_buttons = {}
    
    def _create_sidebar_button(self, parent, text: str, command):
        btn = ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=14),
            height=45,
            anchor="w",
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            command=command
        )
        btn.pack(fill="x", pady=2)
        return btn
    
    def _add_category_button(self, category_name: str):
        if self.category_icon:
            btn = ctk.CTkButton(
                self.categories_frame,
                text=f"  {category_name}",
                image=self.category_icon,
                compound="left",
                font=ctk.CTkFont(size=14),
                height=45,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=lambda: self._on_filter_click(category_name)
            )
        else:
            # Fallback không sử dụng icon
            btn = ctk.CTkButton(
                self.categories_frame,
                text=f"{category_name}",
                font=ctk.CTkFont(size=14),
                height=45,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=lambda: self._on_filter_click(category_name)
            )
        
        btn.pack(fill="x", pady=2)
        self.category_buttons[category_name] = btn
    
    def _on_header_menu_click(self):
        if hasattr(self, 'current_filter'):
            self._show_category_menu(self.current_filter, self.category_menu_btn)
    
    def _show_category_menu(self, category: str, button):
        import tkinter as tk
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Sửa", command=lambda: self._edit_category(category))
        menu.add_command(label="Xóa", command=lambda: self._delete_category(category))
        
        try:
            x = button.winfo_rootx()
            y = button.winfo_rooty() + button.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()
    
    def _edit_category(self, category: str):
        dialog = ctk.CTkInputDialog(
            text=f"Nhập tên mới cho danh mục '{category}':",
            title="Sửa danh mục"
        )
        new_name = dialog.get_input()
        
        if new_name and new_name.strip() and new_name != category:
            if self.on_edit_category:
                self.on_edit_category(category, new_name.strip())
    
    def _delete_category(self, category: str):
        if self.on_delete_category:
            self.on_delete_category(category)
    
    def select_category(self, category_name: str):
        self._on_filter_click(category_name)
    
    def _on_add_category_click(self):
        dialog = ctk.CTkInputDialog(
            text="Nhập tên danh mục mới:",
            title="Thêm danh mục"
        )
        category_name = dialog.get_input()
        
        if category_name and category_name.strip():
            if self.on_add_category:
                success = self.on_add_category(category_name.strip())
                if success:
                    pass
    
    def update_categories(self, categories: list):
        self.available_categories = [cat for cat in categories if cat != FilterType.ALL]
        
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        self.category_buttons.clear()
        
        for category in categories:
            if category != FilterType.ALL:
                self._add_category_button(category)
    
    # ==================== Main Content ====================
    
    def _create_main_content(self):
        self.main_content = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_rowconfigure(2, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        self._create_header()
        self._create_input_area()
        self._create_notes_list()
    
    def _create_header(self):
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(2, weight=1)
        
        self.view_title = ctk.CTkLabel(
            header_frame,
            text="Tất cả ghi chú",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w"
        )
        self.view_title.grid(row=0, column=0, sticky="w")
        
        # Category menu button
        self.category_menu_btn = ctk.CTkButton(
            header_frame,
            text="⋮",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            command=self._on_header_menu_click
        )
        self.category_menu_btn.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.category_menu_btn.grid_remove()
        
        # Count label
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="0 ghi chú",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60"),
            anchor="w"
        )
        self.count_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Search and sort
        tools_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        tools_frame.grid(row=0, column=2, rowspan=2, sticky="e")
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            tools_frame,
            placeholder_text="Tìm kiếm...",
            width=250,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())
        
        # Sort menu
        self.sort_var = ctk.StringVar(value=SortOption.NEWEST)
        self.sort_menu = ctk.CTkOptionMenu(
            tools_frame,
            values=SortOption.all(),
            variable=self.sort_var,
            command=self._on_sort_change,
            width=150,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.sort_menu.pack(side="left")
    
    def _create_input_area(self):
        input_frame = ctk.CTkFrame(self.main_content)
        input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.note_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Thêm ghi chú mới...",
            height=50,
            font=ctk.CTkFont(size=15)
        )
        self.note_input.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.note_input.bind("<Return>", lambda e: self._on_add_click())
        
        if self.add_icon:
            add_btn = ctk.CTkButton(
                input_frame,
                text=" Thêm",
                image=self.add_icon,
                compound="left",
                width=100,
                height=50,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=self.colors['accent'],
                hover_color=self.colors['accent_hover'],
                command=self._on_add_click
            )
        else:
            add_btn = ctk.CTkButton(
                input_frame,
                text="Thêm",
                width=80,
                height=50,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=self.colors['accent'],
                hover_color=self.colors['accent_hover'],
                command=self._on_add_click
            )
        add_btn.grid(row=0, column=1, padx=(0, 10), pady=10)
    
    def _create_notes_list(self):
        self.notes_list_frame = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent"
        )
        self.notes_list_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.notes_list_frame.grid_columnconfigure(0, weight=1)
    
    # ==================== Detail Panel ====================
    
    def _create_detail_panel(self):
        self.detail_panel = ctk.CTkFrame(self.root, width=450, corner_radius=0)
        self.detail_panel.grid_propagate(False)
        self.detail_panel.pack_propagate(False)
        self.detail_panel_visible = False
        
        self.detail_scroll = ctk.CTkScrollableFrame(
            self.detail_panel,
            fg_color="transparent",
            width=400
        )
        self.detail_scroll.pack(fill="both", expand=True, padx=25, pady=20)
        
        close_btn = ctk.CTkButton(
            self.detail_scroll,
            text="✕",
            width=40,
            height=40,
            font=ctk.CTkFont(size=18),
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            command=self.hide_detail_panel
        )
        close_btn.pack(anchor="ne", pady=(0, 10))
        
        self.detail_content_frame = ctk.CTkFrame(
            self.detail_scroll,
            fg_color="transparent"
        )
        self.detail_content_frame.pack(fill="both", expand=True)
    
    # ==================== Display Notes ====================
    
    def display_notes(self, notes: list):
        for widget in self.notes_list_frame.winfo_children():
            widget.destroy()
        
        self.count_label.configure(text=f"{len(notes)} ghi chú")
        
        for note in notes:
            self._create_note_item(note)
        
        if not notes:
            empty_label = ctk.CTkLabel(
                self.notes_list_frame,
                text=Messages.INFO_NO_NOTES,
                font=ctk.CTkFont(size=16),
                text_color=("gray50", "gray60")
            )
            empty_label.pack(pady=50)
    
    def _create_note_item(self, note):
        # Container
        note_frame = ctk.CTkFrame(
            self.notes_list_frame,
            fg_color=("gray85", "gray20"),
            corner_radius=10,
            border_width=1,
            border_color=("gray70", "gray30")
        )
        note_frame.pack(fill="x", pady=5)
        
        # Bind click để xem chi tiết
        note_frame.bind("<Button-1>", lambda e, n=note: self._on_note_click(n))
        
        # Inner frame
        inner_frame = ctk.CTkFrame(note_frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=15, pady=12)
        
        # Priority bar (left side) - Luôn hiển thị để tránh checkbox bị lệch
        priority_color = Colors.get_priority_color(note.priority)
        
        priority_bar = ctk.CTkFrame(
            inner_frame,
            width=4,
            height=40,
            fg_color=priority_color,
            corner_radius=2
        )
        priority_bar.pack(side="left", padx=(0, 10))
        
        # Checkbox
        check_var = ctk.BooleanVar(value=note.is_completed)
        checkbox = ctk.CTkCheckBox(
            inner_frame,
            text="",
            variable=check_var,
            width=24,
            checkbox_width=24,
            checkbox_height=24,
            command=lambda: self._on_toggle_completed(note.note_id)
        )
        checkbox.pack(side="left", padx=(0, 15))
        
        # Text content
        text_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        text_frame.bind("<Button-1>", lambda e, n=note: self._on_note_click(n))
        
        # Title
        title_font = ctk.CTkFont(size=14, overstrike=note.is_completed)
        title_color = ("gray60", "gray60") if note.is_completed else ("gray10", "gray90")
        
        title_label = ctk.CTkLabel(
            text_frame,
            text=note.title,
            font=title_font,
            text_color=title_color,
            anchor="w"
        )
        title_label.pack(anchor="w")
        title_label.bind("<Button-1>", lambda e, n=note: self._on_note_click(n))
        
        # Info row (category, attachments, due date) - chỉ tạo khi có thông tin
        has_info = (note.category != FilterType.ALL) or note.attachments or note.due_date
        
        if has_info:
            info_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
            info_frame.pack(anchor="w", pady=(3, 0))
            
            # Category
            if note.category != FilterType.ALL:
                category_label = ctk.CTkLabel(
                    info_frame,
                    text=f"{note.category}",
                    font=ctk.CTkFont(size=11),
                    text_color=("gray50", "gray60")
                )
                category_label.pack(side="left", padx=(0, 10))
            
            # Attachments
            if note.attachments:
                if self.attachment_icon:
                    attach_label = ctk.CTkLabel(
                        info_frame,
                        text=f" {len(note.attachments)}",
                        image=self.attachment_icon,
                        compound="left",
                        font=ctk.CTkFont(size=11),
                        text_color=("gray50", "gray60")
                    )
                else:
                    attach_label = ctk.CTkLabel(
                        info_frame,
                        text=f"📎 {len(note.attachments)}",
                        font=ctk.CTkFont(size=11),
                        text_color=("gray50", "gray60")
                    )
                attach_label.pack(side="left", padx=(0, 10))
            
            # Due date
            if note.due_date:
                due_color = self._get_due_date_color(note.due_date)
                if self.calendar_icon:
                    due_label = ctk.CTkLabel(
                        info_frame,
                        text=f" {self._format_due_date(note.due_date)}",
                        image=self.calendar_icon,
                        compound="left",
                        font=ctk.CTkFont(size=11),
                        text_color=due_color
                    )
                else:
                    due_label = ctk.CTkLabel(
                        info_frame,
                        text=f"📅 {self._format_due_date(note.due_date)}",
                        font=ctk.CTkFont(size=11),
                        text_color=due_color
                    )
                due_label.pack(side="left", padx=(0, 10))
        
        # Star button (importance - based on priority)
        is_important = note.priority == "Cao"
        
        if self.star_icon and self.star_blank_icon:
            star_btn = ctk.CTkButton(
                inner_frame,
                text="",
                image=self.star_icon if is_important else self.star_blank_icon,
                width=40,
                height=40,
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                command=lambda: self._on_toggle_important(note.note_id)
            )
        else:
            star_text = " "
            star_btn = ctk.CTkButton(
                inner_frame,
                text=star_text,
                width=40,
                height=40,
                font=ctk.CTkFont(size=20),
                fg_color="transparent",
                hover_color=("gray75", "gray25"),
                text_color=self.colors['star'] if is_important else ("gray50", "gray60"),
                command=lambda: self._on_toggle_important(note.note_id)
            )
        star_btn.pack(side="right")
    
    def _get_due_date_color(self, due_date_str: str):
        try:
            due = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            today = date.today()
            
            if due < today:
                return self.colors['danger']  # Quá hạn
            elif due == today:
                return self.colors['warning']  # Hôm nay
            else:
                return self.colors['accent']  # Sắp tới
        except:
            return ("gray50", "gray60")
    
    def _format_due_date(self, due_date_str: str) -> str:
        """Format due date"""
        try:
            due = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            today = date.today()
            
            if due == today:
                return "Hôm nay"
            elif due == today + timedelta(days=1):
                return "Ngày mai"
            elif due < today:
                days_ago = (today - due).days
                return f"Quá {days_ago} ngày"
            else:
                return due.strftime("%d/%m/%Y")
        except:
            return due_date_str
    
    # ==================== Detail Panel ====================
    
    def show_detail_panel(self, note):
        """Hiển thị panel chi tiết ghi chú"""
        self.selected_note_id = note.note_id
        
        # Clear old content
        for widget in self.detail_content_frame.winfo_children():
            widget.destroy()
        
        title_frame = ctk.CTkFrame(self.detail_content_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        check_var = ctk.BooleanVar(value=note.is_completed)
        checkbox = ctk.CTkCheckBox(
            title_frame,
            text="",
            variable=check_var,
            width=32,
            checkbox_width=32,
            checkbox_height=32,
            command=lambda: self._on_toggle_completed(note.note_id)
        )
        checkbox.pack(side="left", padx=(0, 15))
        
        title_font = ctk.CTkFont(size=20, weight="bold", overstrike=note.is_completed)
        self.detail_title_entry = ctk.CTkEntry(
            title_frame,
            font=title_font,
            height=50,
            border_width=0,
            fg_color="transparent"
        )
        self.detail_title_entry.insert(0, note.title)
        self.detail_title_entry.pack(side="left", fill="x", expand=True)
        
        separator = ctk.CTkFrame(
            self.detail_content_frame,
            height=2,
            fg_color=("gray70", "gray30")
        )
        separator.pack(fill="x", pady=15)
        
        # Category
        self._add_detail_section("Danh mục", note.category, "category")
        
        # Priority
        self._add_detail_section("Mức độ ưu tiên", note.priority, "priority")
        
        # Due date
        self._add_detail_section("Ngày đến hạn", note.due_date or "Không có", "due_date")
        
        # Content/Notes
        notes_label = ctk.CTkLabel(
            self.detail_content_frame,
            text="Nội dung",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        notes_label.pack(anchor="w", pady=(20, 5))
        
        self.detail_content_textbox = ctk.CTkTextbox(
            self.detail_content_frame,
            height=200,
            font=ctk.CTkFont(size=14),
            border_width=2,
            border_color=("gray70", "gray30")
        )
        self.detail_content_textbox.pack(fill="both", expand=True, pady=(0, 10))
        self.detail_content_textbox.insert("1.0", note.content or '')
        
        # Attachments
        self._show_attachments_section(note)
        
        # Action buttons
        self._create_action_buttons(note)
        
        # Show panel
        if not self.detail_panel_visible:
            self.detail_panel.grid(row=0, column=2, sticky="nsew")
            self.detail_panel_visible = True
    
    def _add_detail_section(self, label: str, value: str, field_type: str):
        label_widget = ctk.CTkLabel(
            self.detail_content_frame,
            text=label,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        )
        label_widget.pack(anchor="w", pady=(10, 5))
        
        if field_type == "category":
            category_values = self.available_categories if self.available_categories else []
            self.detail_category_menu = ctk.CTkOptionMenu(
                self.detail_content_frame,
                values=category_values,
                height=50,
                font=ctk.CTkFont(size=15)
            )
            self.detail_category_menu.set(value)
            self.detail_category_menu.pack(fill="x", pady=(0, 10))
        
        elif field_type == "priority":
            self.detail_priority_menu = ctk.CTkOptionMenu(
                self.detail_content_frame,
                values=Priority.all(),
                height=50,
                font=ctk.CTkFont(size=15)
            )
            self.detail_priority_menu.set(value)
            self.detail_priority_menu.pack(fill="x", pady=(0, 10))
        
        elif field_type == "due_date":
            date_frame = ctk.CTkFrame(self.detail_content_frame)
            date_frame.pack(fill="x", pady=(0, 10))
            
            self.detail_due_date_entry = ctk.CTkEntry(
                date_frame,
                placeholder_text="YYYY-MM-DD",
                height=50,
                font=ctk.CTkFont(size=15)
            )
            if value != "Không có":
                self.detail_due_date_entry.insert(0, value)
            self.detail_due_date_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            if self.calendar_icon:
                pick_btn = ctk.CTkButton(
                    date_frame,
                    text="",
                    image=self.calendar_icon,
                    width=60,
                    height=50,
                    command=self._pick_due_date
                )
            else:
                pick_btn = ctk.CTkButton(
                    date_frame,
                    text="📅",
                    width=60,
                    height=50,
                    font=ctk.CTkFont(size=18),
                    command=self._pick_due_date
                )
            pick_btn.pack(side="right")
    
    def _show_attachments_section(self, note):
        attach_label = ctk.CTkLabel(
            self.detail_content_frame,
            text=f"Đính kèm ({len(note.attachments)})",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        attach_label.pack(anchor="w", pady=(20, 5))
        
        if self.attachment_icon:
            add_attach_btn = ctk.CTkButton(
                self.detail_content_frame,
                text=" Thêm hình ảnh",
                image=self.attachment_icon,
                compound="left",
                height=40,
                font=ctk.CTkFont(size=13),
                fg_color=("gray85", "gray20"),
                hover_color=("gray75", "gray25"),
                command=lambda: self._on_add_attachment_click(note.note_id)
            )
        else:
            add_attach_btn = ctk.CTkButton(
                self.detail_content_frame,
                text="📎 Thêm hình ảnh",
                height=40,
                font=ctk.CTkFont(size=13),
                fg_color=("gray85", "gray20"),
                hover_color=("gray75", "gray25"),
                command=lambda: self._on_add_attachment_click(note.note_id)
            )
        add_attach_btn.pack(fill="x", pady=(0, 10))
        
        for attachment in note.attachments:
            self._create_attachment_widget(attachment, note.note_id)
    
    def _create_attachment_widget(self, file_path: str, note_id: str):
        """Tạo widget hiển thị file đính kèm"""
        attach_frame = ctk.CTkFrame(self.detail_content_frame)
        attach_frame.pack(fill="x", pady=8)
        
        thumbnail_created = False
        try:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                img = Image.open(file_path)
                img.thumbnail((120, 120))
                photo = ImageTk.PhotoImage(img)
                
                img_button = ctk.CTkButton(
                    attach_frame,
                    image=photo,
                    text="",
                    width=120,
                    height=120,
                    fg_color="transparent",
                    hover_color=("gray85", "gray25"),
                    command=lambda: self._open_image(file_path)
                )
                img_button.image = photo
                img_button.pack(side="left", padx=15, pady=8)
                thumbnail_created = True
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
        
        info_frame = ctk.CTkFrame(attach_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=8)
        
        file_name = os.path.basename(file_path)
        name_label = ctk.CTkLabel(
            info_frame,
            text=file_name,
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        if thumbnail_created:
            open_btn = ctk.CTkButton(
                info_frame,
                text="Xem ảnh",
                width=120,
                height=35,
                font=ctk.CTkFont(size=13),
                fg_color=self.colors['accent'],
                hover_color=self.colors['accent_hover'],
                command=lambda: self._open_image(file_path)
            )
            open_btn.pack(anchor="w", pady=(8, 0))
        
        del_btn = ctk.CTkButton(
            attach_frame,
            text="✕",
            width=40,
            height=40,
            font=ctk.CTkFont(size=16),
            fg_color=self.colors['danger'],
            hover_color="#DC2626",
            command=lambda: self._on_remove_attachment_click(note_id, file_path)
        )
        del_btn.pack(side="right", padx=8)
    
    def _open_image(self, file_path: str):
        try:
            image_window = ctk.CTkToplevel(self.root)
            image_window.title(f"Xem ảnh - {os.path.basename(file_path)}")
            
            img = Image.open(file_path)
            
            max_width = 1000
            max_height = 800
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            image_window.geometry(f"{img.width + 40}x{img.height + 40}")
            
            photo = ImageTk.PhotoImage(img)
            
            img_label = ctk.CTkLabel(
                image_window,
                image=photo,
                text=""
            )
            img_label.image = photo
            img_label.pack(padx=20, pady=20)
            
            image_window.bind("<Escape>", lambda e: image_window.destroy())
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở ảnh: {str(e)}")
    
    def _create_action_buttons(self, note):
        """Tạo các nút hành động"""
        # Save button với save icon
        if self.save_icon:
            save_btn = ctk.CTkButton(
                self.detail_content_frame,
                text=" Lưu thay đổi",
                image=self.save_icon,
                compound="left",
                height=50,
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color=self.colors['success'],
                hover_color="#059669",
                command=lambda: self._on_save_changes(note.note_id)
            )
        else:
            save_btn = ctk.CTkButton(
                self.detail_content_frame,
                text="💾 Lưu thay đổi",
                height=50,
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color=self.colors['success'],
                hover_color="#059669",
                command=lambda: self._on_save_changes(note.note_id)
            )
        save_btn.pack(fill="x", pady=(20, 10))
        
        if self.delete_icon:
            delete_btn = ctk.CTkButton(
                self.detail_content_frame,
                text=" Xóa ghi chú",
                image=self.delete_icon,
                compound="left",
                height=45,
                font=ctk.CTkFont(size=14),
                fg_color=self.colors['danger'],
                hover_color="#DC2626",
                command=lambda: self._on_delete_click(note.note_id)
            )
        else:
            delete_btn = ctk.CTkButton(
                self.detail_content_frame,
                text="🗑 Xóa ghi chú",
                height=45,
                font=ctk.CTkFont(size=14),
                fg_color=self.colors['danger'],
                hover_color="#DC2626",
                command=lambda: self._on_delete_click(note.note_id)
            )
        delete_btn.pack(fill="x", pady=(0, 20))
    
    def hide_detail_panel(self):
        if self.detail_panel_visible:
            self.detail_panel.grid_forget()
            self.detail_panel_visible = False
            self.selected_note_id = None
    
    # ==================== Event Handlers ====================
    
    def _on_filter_click(self, filter_name: str):
        self.current_filter = filter_name
        self.view_title.configure(text=filter_name)
        
        protected_categories = [FilterType.ALL, FilterType.IMPORTANT, FilterType.COMPLETED]
        if filter_name in protected_categories:
            self.category_menu_btn.grid_remove()
        else:
            self.category_menu_btn.grid()
        
        if self.on_filter_change:
            self.on_filter_change(filter_name)
    
    def _on_add_click(self):
        title = self.note_input.get().strip()
        if not title:
            messagebox.showwarning("Cảnh báo", Messages.WARN_TITLE_REQUIRED)
            return
        
        if self.on_add_note:
            self.on_add_note(title, self.current_filter)
            self.note_input.delete(0, 'end')
            self.root.focus()
    
    def _on_note_click(self, note):
        self.show_detail_panel(note)
    
    def _on_toggle_completed(self, note_id: str):
        if self.on_toggle_completed:
            self.on_toggle_completed(note_id)
    
    def _on_toggle_important(self, note_id: str):
        if self.on_toggle_important:
            self.on_toggle_important(note_id)
    
    def _on_save_changes(self, note_id: str):
        try:
            title = self.detail_title_entry.get().strip()
            content = self.detail_content_textbox.get("1.0", "end-1c").strip()
            category = self.detail_category_menu.get()
            priority = self.detail_priority_menu.get()
            due_date = self.detail_due_date_entry.get().strip() or None
            
            if not title:
                messagebox.showwarning("Cảnh báo", Messages.ERROR_TITLE_EMPTY)
                return
            
            if self.on_update_note:
                success = self.on_update_note(
                    note_id,
                    title=title,
                    content=content,
                    category=category,
                    priority=priority,
                    due_date=due_date
                )
                
                if success:
                    messagebox.showinfo("Thành công", Messages.NOTE_UPDATED)
                else:
                    messagebox.showerror("Lỗi", Messages.ERROR_UPDATE_NOTE)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu: {str(e)}")
    
    def _on_delete_click(self, note_id: str):
        result = messagebox.askyesno(
            "Xác nhận xóa",
            Messages.WARN_CONFIRM_DELETE
        )
        
        if result and self.on_delete_note:
            self.on_delete_note(note_id)
            self.hide_detail_panel()
    
    def _on_search(self):
        keyword = self.search_entry.get().strip()
        if self.on_search:
            self.on_search(keyword)
    
    def _on_sort_change(self, choice: str):
        sort_map = SortOption.get_mapping()
        sort_by, reverse = sort_map.get(choice, ("created_at", True))
        
        if self.on_sort_change:
            self.on_sort_change(sort_by, reverse)
    
    def _on_add_attachment_click(self, note_id: str):
        file_path = filedialog.askopenfilename(
            title="Chọn hình ảnh",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path and self.on_add_attachment:
            self.on_add_attachment(note_id, file_path)
    
    def _on_remove_attachment_click(self, note_id: str, file_path: str):
        result = messagebox.askyesno(
            "Xác nhận xóa",
            Messages.WARN_CONFIRM_DELETE_ATTACHMENT
        )
        
        if result and self.on_remove_attachment:
            self.on_remove_attachment(note_id, file_path)
    
    def _on_add_task(self, note):
        task_title = self.new_task_entry.get().strip()
        if not task_title:
            return
        
        if self.on_add_task:
            self.on_add_task(note.note_id, task_title)
            self.new_task_entry.delete(0, 'end')
    
    def _on_delete_task(self, note, task_id: str):
        if self.on_delete_task:
            self.on_delete_task(note.note_id, task_id)
    
    def _on_toggle_task(self, note, task_id: str):
        if self.on_toggle_task:
            self.on_toggle_task(note.note_id, task_id)
    
    def _pick_due_date(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Chọn ngày đến hạn")
        dialog.geometry("350x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(
            dialog,
            text="Chọn ngày đến hạn:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.pack(pady=20)
        
        cal_frame = ctk.CTkFrame(dialog)
        cal_frame.pack(pady=10)
        
        cal = DateEntry(
            cal_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        cal.pack(padx=20, pady=10)
        
        def select_date():
            selected = cal.get_date()
            self.detail_due_date_entry.delete(0, 'end')
            self.detail_due_date_entry.insert(0, selected.strftime("%Y-%m-%d"))
            dialog.destroy()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        select_btn = ctk.CTkButton(
            btn_frame,
            text="Chọn",
            command=select_date,
            width=100
        )
        select_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Hủy",
            command=dialog.destroy,
            fg_color="gray",
            width=100
        )
        cancel_btn.pack(side="left", padx=10)
    
    # ==================== Utility Methods ====================
    
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)
    
    def update_view_title(self, title: str):
        self.view_title.configure(text=title)
