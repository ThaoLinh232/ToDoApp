"""
View: MainView
Giao diện chính của ứng dụng (Microsoft To Do style)
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date, timedelta
from typing import Optional, Callable
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import os


class MainView:
    """Lớp giao diện chính"""
    
    def __init__(self, root: ctk.CTk):
        """
        Khởi tạo giao diện
        
        Args:
            root: Cửa sổ chính CTk
        """
        self.root = root
        self.root.title("Ghi Chú - Microsoft To Do Style")
        self.root.geometry("1400x900")  # Kích thước vừa phải: 250 + 450 + 700 = 1400
        
        # Callbacks (sẽ được set từ controller)
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
        
        # State
        self.selected_note_id: Optional[str] = None
        self.current_filter = "Tất cả"
        
        # Colors (Microsoft To Do style)
        self.colors = {
            'accent': '#3B82F6',
            'accent_hover': '#60A5FA',
            'success': '#10B981',
            'danger': '#EF4444',
            'warning': '#F59E0B',
            'star': '#FBBF24',
            'priority_high': '#EF4444',
            'priority_medium': '#F59E0B',
            'priority_low': '#3B82F6',
            'priority_normal': '#6B7280',
        }
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Thiết lập giao diện"""
        # Configure grid - column 0: sidebar trái, column 1: main content, column 2: detail panel phải
        self.root.grid_columnconfigure(0, weight=0, minsize=250)  # Sidebar trái cố định
        self.root.grid_columnconfigure(1, weight=1)  # Main content co giãn để lấp đầy
        self.root.grid_columnconfigure(2, weight=0)  # Detail panel phải (không weight để không chiếm không gian khi ẩn)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main sections
        self._create_sidebar()
        self._create_main_content()
        self._create_detail_panel()
    
    # ==================== Sidebar ====================
    
    def _create_sidebar(self):
        """Tạo thanh bên trái (sidebar)"""
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # App title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="📝 Ghi Chú",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(30, 20), padx=20)
        
        # Smart views
        views_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        views_frame.pack(fill="x", padx=10, pady=10)
        
        self._create_sidebar_button(
            views_frame, 
            "📋 Tất cả", 
            lambda: self._on_filter_click("Tất cả")
        )
        self._create_sidebar_button(
            views_frame, 
            "⭐ Quan trọng", 
            lambda: self._on_filter_click("Quan trọng")
        )
        self._create_sidebar_button(
            views_frame, 
            "✓ Hoàn thành", 
            lambda: self._on_filter_click("Hoàn thành")
        )
        
        # Separator
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", padx=20, pady=15)
        
        # Categories section
        categories_label = ctk.CTkLabel(
            self.sidebar,
            text="Chủ đề",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        categories_label.pack(fill="x", padx=20, pady=(10, 5))
        
        # Categories list (scrollable)
        self.categories_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent"
        )
        self.categories_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Default categories
        self.category_buttons = {}
        self._add_category_button("💼 Công việc")
        self._add_category_button("👤 Cá nhân")
        self._add_category_button("📚 Học tập")
        self._add_category_button("🏠 Gia đình")
    
    def _create_sidebar_button(self, parent, text: str, command):
        """Tạo nút trong sidebar"""
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
    
    def _add_category_button(self, text: str):
        """Thêm nút category"""
        category = text.split(" ", 1)[1] if " " in text else text
        btn = self._create_sidebar_button(
            self.categories_frame,
            text,
            lambda: self._on_filter_click(category)
        )
        self.category_buttons[category] = btn
    
    def update_categories(self, categories: list):
        """Cập nhật danh sách chủ đề"""
        # Xóa các button cũ
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        self.category_buttons.clear()
        
        # Thêm các category mới
        icons = {
            "Công việc": "💼",
            "Cá nhân": "👤",
            "Học tập": "📚",
            "Gia đình": "🏠",
            "Sức khỏe": "❤️",
            "Mua sắm": "🛒",
            "Du lịch": "✈️",
        }
        
        for category in categories:
            if category != "Tất cả":
                icon = icons.get(category, "📌")
                self._add_category_button(f"{icon} {category}")
    
    # ==================== Main Content ====================
    
    def _create_main_content(self):
        """Tạo khu vực nội dung chính (giữa)"""
        self.main_content = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_rowconfigure(2, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Header
        self._create_header()
        
        # Input area
        self._create_input_area()
        
        # Notes list
        self._create_notes_list()
    
    def _create_header(self):
        """Tạo header với tiêu đề và công cụ"""
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        self.view_title = ctk.CTkLabel(
            header_frame,
            text="Tất cả ghi chú",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w"
        )
        self.view_title.grid(row=0, column=0, sticky="w")
        
        # Count label
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="0 ghi chú",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60"),
            anchor="w"
        )
        self.count_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Search and sort
        tools_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        tools_frame.grid(row=0, column=1, rowspan=2, sticky="e")
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            tools_frame,
            placeholder_text="🔍 Tìm kiếm...",
            width=250,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())
        
        # Sort menu
        self.sort_var = ctk.StringVar(value="Mới nhất")
        self.sort_menu = ctk.CTkOptionMenu(
            tools_frame,
            values=["Mới nhất", "Cũ nhất", "Tên A-Z", "Tên Z-A", "Ưu tiên cao", "Ngày đến hạn"],
            variable=self.sort_var,
            command=self._on_sort_change,
            width=150,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.sort_menu.pack(side="left")
    
    def _create_input_area(self):
        """Tạo khu vực nhập ghi chú mới"""
        input_frame = ctk.CTkFrame(self.main_content)
        input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Input entry
        self.note_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="+ Thêm ghi chú mới...",
            height=50,
            font=ctk.CTkFont(size=15)
        )
        self.note_input.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.note_input.bind("<Return>", lambda e: self._on_add_click())
        
        # Add button
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
        """Tạo danh sách ghi chú (scrollable)"""
        # Scrollable frame
        self.notes_list_frame = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent"
        )
        self.notes_list_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.notes_list_frame.grid_columnconfigure(0, weight=1)
    
    # ==================== Detail Panel ====================
    
    def _create_detail_panel(self):
        """Tạo panel chi tiết ghi chú (bên phải)"""
        self.detail_panel = ctk.CTkFrame(self.root, width=700, corner_radius=0)
        self.detail_panel.grid_propagate(False)  # Giữ width cố định
        self.detail_panel.pack_propagate(False)  # Không cho content làm thay đổi kích thước
        # Ẩn ban đầu
        self.detail_panel_visible = False
        
        # Scrollable content - giảm padding để tận dụng không gian
        self.detail_scroll = ctk.CTkScrollableFrame(
            self.detail_panel,
            fg_color="transparent",
            width=640  # Width rõ ràng (700 - 60 padding)
        )
        self.detail_scroll.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Close button
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
        
        # Content will be created dynamically
        self.detail_content_frame = ctk.CTkFrame(
            self.detail_scroll,
            fg_color="transparent"
        )
        self.detail_content_frame.pack(fill="both", expand=True)
    
    # ==================== Display Notes ====================
    
    def display_notes(self, notes: list):
        """Hiển thị danh sách ghi chú"""
        # Xóa các widget cũ
        for widget in self.notes_list_frame.winfo_children():
            widget.destroy()
        
        # Cập nhật count
        self.count_label.configure(text=f"{len(notes)} ghi chú")
        
        # Hiển thị từng ghi chú
        for note in notes:
            self._create_note_item(note)
        
        # Hiển thị thông báo nếu rỗng
        if not notes:
            empty_label = ctk.CTkLabel(
                self.notes_list_frame,
                text="Chưa có ghi chú nào",
                font=ctk.CTkFont(size=16),
                text_color=("gray50", "gray60")
            )
            empty_label.pack(pady=50)
    
    def _create_note_item(self, note):
        """Tạo widget cho một ghi chú"""
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
        priority_colors = {
            "Cao": self.colors['priority_high'],
            "Trung bình": self.colors['priority_medium'],
            "Thấp": self.colors['priority_low'],
            "Bình thường": self.colors['priority_normal']
        }
        
        priority_bar = ctk.CTkFrame(
            inner_frame,
            width=4,
            height=40,
            fg_color=priority_colors.get(note.priority, self.colors['priority_normal']),
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
        
        # Info row (category, attachments, created date)
        info_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
        info_frame.pack(anchor="w", pady=(3, 0))
        
        # Category
        if note.category != "Tất cả":
            category_label = ctk.CTkLabel(
                info_frame,
                text=f"📁 {note.category}",
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray60")
            )
            category_label.pack(side="left", padx=(0, 10))
        
        # Attachments
        if note.attachments:
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
            due_label = ctk.CTkLabel(
                info_frame,
                text=f"📅 {self._format_due_date(note.due_date)}",
                font=ctk.CTkFont(size=11),
                text_color=due_color
            )
            due_label.pack(side="left", padx=(0, 10))
        
        # Created date
        created_text = note.created_at.strftime("%d/%m/%Y")
        created_label = ctk.CTkLabel(
            info_frame,
            text=created_text,
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        )
        created_label.pack(side="left")
        
        # Star button (importance)
        star_text = "⭐" if note.is_important else "☆"
        star_btn = ctk.CTkButton(
            inner_frame,
            text=star_text,
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            text_color=self.colors['star'] if note.is_important else ("gray50", "gray60"),
            command=lambda: self._on_toggle_important(note.note_id)
        )
        star_btn.pack(side="right")
    
    def _get_due_date_color(self, due_date_str: str):
        """Lấy màu cho due date"""
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
        
        # Title with checkbox
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
        
        # Title entry
        title_font = ctk.CTkFont(size=24, weight="bold", overstrike=note.is_completed)
        self.detail_title_entry = ctk.CTkEntry(
            title_frame,
            font=title_font,
            height=55,
            border_width=0,
            fg_color="transparent"
        )
        self.detail_title_entry.insert(0, note.title)
        self.detail_title_entry.pack(side="left", fill="x", expand=True)
        
        # Separator
        separator = ctk.CTkFrame(
            self.detail_content_frame,
            height=2,
            fg_color=("gray70", "gray30")
        )
        separator.pack(fill="x", pady=15)
        
        # Important button
        star_text = "⭐ Bỏ đánh dấu quan trọng" if note.is_important else "☆ Đánh dấu quan trọng"
        star_btn = ctk.CTkButton(
            self.detail_content_frame,
            text=star_text,
            font=ctk.CTkFont(size=13),
            height=45,
            anchor="w",
            fg_color=("gray85", "gray20"),
            hover_color=("gray75", "gray25"),
            command=lambda: self._on_toggle_important(note.note_id)
        )
        star_btn.pack(fill="x", pady=(0, 10))
        
        # Category
        self._add_detail_section("Chủ đề", note.category, "category")
        
        # Priority
        self._add_detail_section("Mức độ ưu tiên", note.priority, "priority")
        
        # Due date
        self._add_detail_section("Ngày đến hạn", note.due_date or "Không có", "due_date")
        
        # Reminder
        if note.reminder:
            self._add_detail_section("Lời nhắc", note.reminder, "reminder")
        
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
            height=300,
            font=ctk.CTkFont(size=15),
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
        """Thêm section trong detail panel"""
        label_widget = ctk.CTkLabel(
            self.detail_content_frame,
            text=label,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        )
        label_widget.pack(anchor="w", pady=(10, 5))
        
        if field_type == "category":
            categories = ["Tất cả", "Công việc", "Cá nhân", "Học tập", "Gia đình", "Sức khỏe", "Mua sắm", "Du lịch"]
            self.detail_category_menu = ctk.CTkOptionMenu(
                self.detail_content_frame,
                values=categories,
                height=50,
                font=ctk.CTkFont(size=15)
            )
            self.detail_category_menu.set(value)
            self.detail_category_menu.pack(fill="x", pady=(0, 10))
        
        elif field_type == "priority":
            priorities = ["Bình thường", "Thấp", "Trung bình", "Cao"]
            self.detail_priority_menu = ctk.CTkOptionMenu(
                self.detail_content_frame,
                values=priorities,
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
        """Hiển thị section đính kèm"""
        attach_label = ctk.CTkLabel(
            self.detail_content_frame,
            text=f"Đính kèm ({len(note.attachments)})",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        attach_label.pack(anchor="w", pady=(20, 5))
        
        # Add attachment button
        add_attach_btn = ctk.CTkButton(
            self.detail_content_frame,
            text="📎 Thêm hình ảnh",
            height=50,
            font=ctk.CTkFont(size=14),
            fg_color=("gray85", "gray20"),
            hover_color=("gray75", "gray25"),
            command=lambda: self._on_add_attachment_click(note.note_id)
        )
        add_attach_btn.pack(fill="x", pady=(0, 10))
        
        # Display attachments
        for attachment in note.attachments:
            self._create_attachment_widget(attachment, note.note_id)
    
    def _create_attachment_widget(self, file_path: str, note_id: str):
        """Tạo widget hiển thị file đính kèm"""
        attach_frame = ctk.CTkFrame(self.detail_content_frame)
        attach_frame.pack(fill="x", pady=8)
        
        # Try to load thumbnail
        thumbnail_created = False
        try:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                img = Image.open(file_path)
                img.thumbnail((120, 120))  # Tăng kích thước thumbnail
                photo = ImageTk.PhotoImage(img)
                
                # Create clickable thumbnail button
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
                img_button.image = photo  # Keep reference
                img_button.pack(side="left", padx=15, pady=8)
                thumbnail_created = True
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
        
        # File info frame
        info_frame = ctk.CTkFrame(attach_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=8)
        
        # File name
        file_name = os.path.basename(file_path)
        name_label = ctk.CTkLabel(
            info_frame,
            text=file_name,
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Open button (for images)
        if thumbnail_created:
            open_btn = ctk.CTkButton(
                info_frame,
                text="🔍 Xem ảnh",
                width=120,
                height=35,
                font=ctk.CTkFont(size=13),
                fg_color=self.colors['accent'],
                hover_color=self.colors['accent_hover'],
                command=lambda: self._open_image(file_path)
            )
            open_btn.pack(anchor="w", pady=(8, 0))
        
        # Delete button
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
        """Mở ảnh trong cửa sổ mới"""
        try:
            # Tạo cửa sổ mới để hiển thị ảnh
            image_window = ctk.CTkToplevel(self.root)
            image_window.title(f"Xem ảnh - {os.path.basename(file_path)}")
            
            # Load ảnh gốc
            img = Image.open(file_path)
            
            # Resize để vừa màn hình nhưng giữ tỷ lệ
            max_width = 1000
            max_height = 800
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Set kích thước cửa sổ dựa trên kích thước ảnh
            image_window.geometry(f"{img.width + 40}x{img.height + 40}")
            
            # Hiển thị ảnh
            photo = ImageTk.PhotoImage(img)
            
            img_label = ctk.CTkLabel(
                image_window,
                image=photo,
                text=""
            )
            img_label.image = photo  # Keep reference
            img_label.pack(padx=20, pady=20)
            
            # Cho phép đóng bằng phím Escape
            image_window.bind("<Escape>", lambda e: image_window.destroy())
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở ảnh: {str(e)}")
    
    def _create_action_buttons(self, note):
        """Tạo các nút hành động"""
        # Save button
        # Save button
        save_btn = ctk.CTkButton(
            self.detail_content_frame,
            text="💾 Lưu thay đổi",
            height=60,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors['success'],
            hover_color="#059669",
            command=lambda: self._on_save_changes(note.note_id)
        )
        save_btn.pack(fill="x", pady=(25, 12))
        
        # Delete button
        delete_btn = ctk.CTkButton(
            self.detail_content_frame,
            text="🗑 Xóa ghi chú",
            height=55,
            font=ctk.CTkFont(size=15),
            fg_color=self.colors['danger'],
            hover_color="#DC2626",
            command=lambda: self._on_delete_click(note.note_id)
        )
        delete_btn.pack(fill="x", pady=(0, 25))
        delete_btn.pack(fill="x", pady=(0, 20))
    
    def hide_detail_panel(self):
        """Ẩn panel chi tiết"""
        if self.detail_panel_visible:
            self.detail_panel.grid_forget()
            self.detail_panel_visible = False
            self.selected_note_id = None
    
    # ==================== Event Handlers ====================
    
    def _on_filter_click(self, filter_name: str):
        """Xử lý khi click vào bộ lọc"""
        self.current_filter = filter_name
        # Update title
        icons = {
            "Tất cả": "📋",
            "Quan trọng": "⭐",
            "Hoàn thành": "✓"
        }
        icon = icons.get(filter_name, "📁")
        self.view_title.configure(text=f"{icon} {filter_name}")
        
        # Call callback
        if self.on_filter_change:
            self.on_filter_change(filter_name)
    
    def _on_add_click(self):
        """Xử lý khi click nút Thêm"""
        title = self.note_input.get().strip()
        if not title:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tiêu đề ghi chú!")
            return
        
        if self.on_add_note:
            self.on_add_note(title, self.current_filter)
            self.note_input.delete(0, 'end')
            self.root.focus()
    
    def _on_note_click(self, note):
        """Xử lý khi click vào ghi chú"""
        self.show_detail_panel(note)
    
    def _on_toggle_completed(self, note_id: str):
        """Xử lý toggle hoàn thành"""
        if self.on_toggle_completed:
            self.on_toggle_completed(note_id)
    
    def _on_toggle_important(self, note_id: str):
        """Xử lý toggle quan trọng"""
        if self.on_toggle_important:
            self.on_toggle_important(note_id)
    
    def _on_save_changes(self, note_id: str):
        """Xử lý lưu thay đổi"""
        try:
            title = self.detail_title_entry.get().strip()
            content = self.detail_content_textbox.get("1.0", "end-1c").strip()
            category = self.detail_category_menu.get()
            priority = self.detail_priority_menu.get()
            due_date = self.detail_due_date_entry.get().strip() or None
            
            if not title:
                messagebox.showwarning("Cảnh báo", "Tiêu đề không được để trống!")
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
                    messagebox.showinfo("Thành công", "Đã lưu thay đổi!")
                else:
                    messagebox.showerror("Lỗi", "Không thể lưu thay đổi!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu: {str(e)}")
    
    def _on_delete_click(self, note_id: str):
        """Xử lý xóa ghi chú"""
        result = messagebox.askyesno(
            "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa ghi chú này?\nThao tác này không thể hoàn tác!"
        )
        
        if result and self.on_delete_note:
            self.on_delete_note(note_id)
            self.hide_detail_panel()
    
    def _on_search(self):
        """Xử lý tìm kiếm"""
        keyword = self.search_entry.get().strip()
        if self.on_search:
            self.on_search(keyword)
    
    def _on_sort_change(self, choice: str):
        """Xử lý thay đổi sắp xếp"""
        sort_map = {
            "Mới nhất": ("created_at", True),
            "Cũ nhất": ("created_at", False),
            "Tên A-Z": ("title", False),
            "Tên Z-A": ("title", True),
            "Ưu tiên cao": ("priority", False),
            "Ngày đến hạn": ("due_date", False)
        }
        
        sort_by, reverse = sort_map.get(choice, ("created_at", True))
        
        if self.on_sort_change:
            self.on_sort_change(sort_by, reverse)
    
    def _on_add_attachment_click(self, note_id: str):
        """Xử lý thêm đính kèm"""
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
        """Xử lý xóa đính kèm"""
        result = messagebox.askyesno(
            "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa file đính kèm này?"
        )
        
        if result and self.on_remove_attachment:
            self.on_remove_attachment(note_id, file_path)
    
    def _pick_due_date(self):
        """Chọn ngày đến hạn bằng calendar"""
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
        
        # Calendar
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
        
        # Buttons
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
        """Hiển thị thông báo"""
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)
    
    def update_view_title(self, title: str):
        """Cập nhật tiêu đề view"""
        self.view_title.configure(text=title)
