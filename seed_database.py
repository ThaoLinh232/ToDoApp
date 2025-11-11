"""
Seed Database - Tạo dữ liệu mẫu cho testing
"""

import mysql.connector
from datetime import datetime, timedelta
import random
import uuid

# Cấu hình database
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'todo_app_mvc',
    'charset': 'utf8mb4'
}

def seed_database():
    """Seed database với dữ liệu mẫu đa dạng"""
    
    print("=" * 70)
    print("DATABASE SEEDING - Tạo dữ liệu mẫu")
    print("=" * 70)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Lấy categories
        cursor.execute("SELECT category_id, category_name FROM categories")
        categories = {row['category_name']: row['category_id'] for row in cursor.fetchall()}
        
        # Lấy priorities
        cursor.execute("SELECT priority_id, priority_name FROM priorities")
        priorities = {row['priority_name']: row['priority_id'] for row in cursor.fetchall()}
        
        print("\n📊 Categories và Priorities đã có:")
        print(f"   • Categories: {', '.join(categories.keys())}")
        print(f"   • Priorities: {', '.join(priorities.keys())}")
        
        # Tạo tags mẫu
        print("\n🏷️  Tạo tags mẫu...")
        sample_tags = [
            ('urgent', '#EF4444'),
            ('meeting', '#F59E0B'),
            ('project', '#3B82F6'),
            ('review', '#8B5CF6'),
            ('deadline', '#DC2626'),
            ('planning', '#10B981'),
            ('personal', '#EC4899'),
            ('learning', '#F97316'),
            ('health', '#14B8A6'),
            ('finance', '#6366F1')
        ]
        
        tag_ids = {}
        for tag_name, tag_color in sample_tags:
            cursor.execute(
                "INSERT IGNORE INTO tags (tag_name, tag_color) VALUES (%s, %s)",
                (tag_name, tag_color)
            )
            conn.commit()
            
            cursor.execute("SELECT tag_id FROM tags WHERE tag_name = %s", (tag_name,))
            tag_ids[tag_name] = cursor.fetchone()['tag_id']
        
        print(f"   ✓ Đã tạo {len(sample_tags)} tags")
        
        # Tạo notes mẫu
        print("\n📝 Tạo notes mẫu...")
        
        sample_notes = [
            # Công việc
            {
                'title': 'Hoàn thành báo cáo Q4 2025',
                'content': '''Nội dung báo cáo:
- Tổng hợp dữ liệu từ các phòng ban
- Phân tích xu hướng và KPI
- So sánh với Q4 2024
- Đề xuất chiến lược 2026

Deadline: 30/10/2025
Người nhận: Ban Giám Đốc''',
                'category': 'Công việc',
                'priority': 'Cao',
                'is_important': True,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=6),
                'tags': ['urgent', 'deadline', 'project']
            },
            {
                'title': 'Họp team Sprint Planning',
                'content': '''Meeting details:
📅 Thời gian: Thứ 2, 9:00 AM
📍 Địa điểm: Phòng họp tầng 3
👥 Người tham gia: Full team + PO

Agenda:
1. Review Sprint trước (30 phút)
2. Planning Sprint mới (60 phút)
3. Estimate story points (30 phút)
4. Q&A (15 phút)

Chuẩn bị: Laptop, danh sách User Stories''',
                'category': 'Công việc',
                'priority': 'Trung bình',
                'is_important': True,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=3),
                'tags': ['meeting', 'planning']
            },
            {
                'title': 'Review code module thanh toán',
                'content': '''Pull Request #234 - Payment Gateway Integration

Cần review:
✓ Kiểm tra security (SQL injection, XSS)
✓ Performance optimization
✓ Error handling
✓ Unit tests coverage (>80%)
✓ Documentation

Files changed: 15
Lines: +342 -127

Assignee: @john_dev
Reviewer: Me''',
                'category': 'Công việc',
                'priority': 'Cao',
                'is_important': True,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=1),
                'tags': ['review', 'urgent']
            },
            
            # Học tập
            {
                'title': 'Khóa học Python Advanced - Week 3',
                'content': '''Tiến độ học tập:
✅ Week 1: Decorators và Generators
✅ Week 2: Context Managers và Async/Await
🔄 Week 3: Metaclasses (đang học)
☐ Week 4: Design Patterns
☐ Week 5: Performance Optimization

Bài tập tuần này:
- Implement Custom Metaclass
- Build Singleton Pattern
- Create ORM mini framework

Deadline: 27/10/2025''',
                'category': 'Học tập',
                'priority': 'Trung bình',
                'is_important': True,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=3),
                'tags': ['learning', 'project']
            },
            {
                'title': 'Đọc sách "Clean Architecture"',
                'content': '''📚 Robert C. Martin

Tiến độ: 180/420 trang (43%)

Chương đã đọc:
✓ Part I: Introduction
✓ Part II: Programming Paradigms
✓ Part III: Design Principles (SOLID)
🔄 Part IV: Component Principles

Ghi chú quan trọng:
- Dependency Rule
- Screaming Architecture
- Humble Object Pattern
- Boundary Crossing

Mục tiêu: 50 trang/tuần''',
                'category': 'Học tập',
                'priority': 'Thấp',
                'is_important': False,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=14),
                'tags': ['learning', 'personal']
            },
            
            # Sức khỏe
            {
                'title': 'Lịch tập gym tuần này',
                'content': '''💪 Workout Schedule

Thứ 2, 4, 6: Upper Body
- Warm up: 10 phút cardio
- Bench Press: 4 sets x 10 reps
- Shoulder Press: 3 sets x 12 reps
- Bicep Curls: 3 sets x 15 reps
- Tricep Dips: 3 sets x 12 reps
- Cool down: Stretching 10 phút

Thứ 3, 5, 7: Lower Body + Core
- Warm up: 10 phút treadmill
- Squats: 4 sets x 10 reps
- Deadlifts: 3 sets x 8 reps
- Lunges: 3 sets x 12 reps mỗi chân
- Plank: 3 sets x 1 phút
- Core workout: 15 phút

Chủ nhật: Rest day 😴''',
                'category': 'Sức khỏe',
                'priority': 'Trung bình',
                'is_important': True,
                'is_completed': False,
                'due_date': None,
                'tags': ['health', 'personal']
            },
            {
                'title': 'Đặt lịch khám sức khỏe định kỳ',
                'content': '''🏥 Medical Checkup

Bệnh viện: Vinmec Times City
Gói khám: Tổng quát plus

Danh sách xét nghiệm:
✓ Xét nghiệm máu tổng quát
✓ Đường huyết
✓ Cholesterol
✓ Chức năng gan, thận
✓ Siêu âm bụng tổng quát
✓ X-quang phổi
✓ Khám mắt, răng miệng

Lần khám trước: 24/04/2025
Lần khám tiếp: 24/10/2025 (hôm nay!)

☎️ Hotline: 1900 xxxx''',
                'category': 'Sức khỏe',
                'priority': 'Cao',
                'is_important': True,
                'is_completed': False,
                'due_date': datetime.now(),
                'tags': ['health', 'urgent']
            },
            
            # Mua sắm
            {
                'title': 'Danh sách mua sắm cuối tuần',
                'content': '''🛒 Shopping List

Thực phẩm tươi sống:
☐ Rau củ quả (cải, cà rốt, khoai tây, cà chua)
☐ Thịt gà: 1kg
☐ Cá hồi: 500g
☐ Trứng gà: 1 hộp (10 quả)

Thực phẩm khô:
☐ Gạo: 5kg (ST25)
☐ Dầu ăn: 1 chai
☐ Nước mắm, nước tương
☐ Mì gói: 1 thùng

Đồ dùng:
☐ Giấy vệ sinh: 1 lốc
☐ Nước rửa chén
☐ Bột giặt

Budget: ~1.500.000 VNĐ
Siêu thị: VinMart hoặc Mega Market''',
                'category': 'Mua sắm',
                'priority': 'Trung bình',
                'is_important': False,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=2),
                'tags': ['personal']
            },
            {
                'title': 'Mua quà sinh nhật bạn',
                'content': '''🎁 Birthday Gift Ideas

Người nhận: Sarah
Sinh nhật: 28/10/2025
Budget: 1-2 triệu

Ý tưởng:
1. Sách: "Atomic Habits" + "The Psychology of Money"
2. Voucher spa/massage
3. Đồng hồ thông minh (Xiaomi Band)
4. Bộ mỹ phẩm (The Body Shop)
5. Voucher nhà hàng + rạp phim

✨ Quyết định: Sách + Voucher spa (1.5M)

Địa điểm mua:
- Sách: Fahasa online
- Voucher: Klook/Shopee''',
                'category': 'Mua sắm',
                'priority': 'Cao',
                'is_important': True,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=4),
                'tags': ['personal', 'deadline']
            },
            
            # Gia đình
            {
                'title': 'Gọi điện về nhà',
                'content': '''📞 Weekly Family Call

Danh sách cần hỏi:
✓ Sức khỏe bố mẹ
✓ Tình hình công việc nhà
✓ Em trai học hành thế nào
✓ Kế hoạch về nhà cuối tuần

Gửi tiền về: 5.000.000 VNĐ
Chuyển khoản ngày 25 hàng tháng

Lần gọi trước: 17/10/2025
Lần gọi tiếp: Chủ nhật này''',
                'category': 'Gia đình',
                'priority': 'Cao',
                'is_important': True,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=3),
                'tags': ['personal']
            },
            {
                'title': 'Chuẩn bị về nhà nghỉ lễ',
                'content': '''🏠 Holiday Planning

Thời gian: 2-3/11 (2 ngày 1 đêm)
Phương tiện: Xe khách (Phương Trang)

Cần chuẩn bị:
☐ Đặt vé xe trước (online)
☐ Mua quà cho bố mẹ
☐ Mua đồ ăn vặt về nhà
☐ Kiểm tra lịch công việc
☐ Xin phép sếp

Quà tặng:
- Bố: Rượu + Thuốc xoa bóp
- Mẹ: Mỹ phẩm + Áo dài
- Em: Giày thể thao + Sách

Budget: 3.000.000 VNĐ''',
                'category': 'Gia đình',
                'priority': 'Trung bình',
                'is_important': True,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=8),
                'tags': ['planning', 'personal']
            },
            
            # Cá nhân
            {
                'title': 'Lên kế hoạch tài chính tháng 11',
                'content': '''💰 Financial Planning

Thu nhập tháng 11 (dự kiến): 25.000.000 VNĐ

Chi tiêu cố định:
- Tiền nhà: 6.000.000
- Ăn uống: 4.000.000
- Đi lại: 1.500.000
- Điện nước: 800.000
- Internet: 200.000
Tổng: 12.500.000

Chi tiêu khác:
- Gym: 1.000.000
- Sách/Khóa học: 1.000.000
- Giải trí: 1.500.000
- Dự phòng: 1.000.000
Tổng: 4.500.000

Tiết kiệm: 5.000.000
Gửi về nhà: 3.000.000

Tổng chi: 25.000.000 ✓

Mục tiêu: Tiết kiệm 60M trong 2025''',
                'category': 'Cá nhân',
                'priority': 'Trung bình',
                'is_important': True,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=7),
                'tags': ['finance', 'planning', 'personal']
            },
            {
                'title': 'Viết blog về Design Patterns',
                'content': '''✍️ Blog Post Draft

Topic: "5 Design Patterns Thường Gặp Trong Thực Tế"

Outline:
1. Singleton Pattern
   - Khái niệm
   - Use cases
   - Code example (Python)
   - Pros & Cons

2. Factory Pattern
   - Problem it solves
   - Implementation
   - Real-world example

3. Observer Pattern
   - Event-driven programming
   - Publisher-Subscriber
   - Example: GUI frameworks

4. Decorator Pattern
   - Extend functionality
   - Python decorators
   - Use cases

5. Strategy Pattern
   - Behavior selection
   - Dependency Injection
   - Testing benefits

Target: 3000-4000 words
Platform: Medium + Dev.to
Deadline: 31/10/2025''',
                'category': 'Cá nhân',
                'priority': 'Thấp',
                'is_important': False,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=7),
                'tags': ['learning', 'project', 'personal']
            },
            
            # Du lịch
            {
                'title': 'Lên kế hoạch du lịch Đà Lạt',
                'content': '''🏔️ Đà Lạt Trip Planning

Thời gian: 15-17/12/2025 (3 ngày 2 đêm)
Số người: 4 người
Budget/người: 3.000.000 VNĐ

Lịch trình:
Day 1: HN → Đà Lạt
- Bay sáng (7h) - VietJet
- Check-in khách sạn
- Chiều: Hồ Xuân Hương, Chợ Đà Lạt
- Tối: Quán cafe acoustic

Day 2: Tour trong thành phố
- Sáng: Thiền viện Trúc Lâm, Langbiang
- Trưa: Ăn lẩu gà lá é
- Chiều: Đường hầm Đất Sét, Quán Gió
- Tối: BBQ tại villa

Day 3: Đà Lạt → HN
- Sáng: Chợ sáng, mua đặc sản
- Bay chiều (15h)

Cần book:
☐ Vé máy bay (4 vé khứ hồi)
☐ Villa/Hotel 2 đêm
☐ Thuê xe máy (4 xe)
☐ Tour Langbiang

Đặc sản mua về:
- Atiso, dâu tây, rau
- Mứt, sữa chua
- Cafe hạt rang''',
                'category': 'Du lịch',
                'priority': 'Thấp',
                'is_important': False,
                'is_completed': False,
                'due_date': datetime.now() + timedelta(days=52),
                'tags': ['planning', 'personal']
            },
            
            # Đã hoàn thành
            {
                'title': 'Renew driving license',
                'content': '''✅ Đã đổi bằng lái xe thành công

Trung tâm: Sở GTVT Hà Nội
Thời gian: 20/10/2025
Phí: 270.000 VNĐ

Hồ sơ đã nộp:
✓ CMND/CCCD
✓ Bằng lái cũ
✓ Giấy khám sức khỏe
✓ 2 ảnh 3x4

Bằng mới có hiệu lực đến: 20/10/2035

Note: Đã update ảnh và địa chỉ mới''',
                'category': 'Cá nhân',
                'priority': 'Bình thường',
                'is_important': False,
                'is_completed': True,
                'due_date': None,
                'tags': ['personal']
            },
            {
                'title': 'Backup dữ liệu laptop',
                'content': '''💾 Backup Completed

Ngày backup: 22/10/2025
Target: External HDD 2TB (Seagate)

Dữ liệu đã backup:
✓ Documents (50GB)
✓ Projects/Code (30GB)
✓ Photos (120GB)
✓ Videos (80GB)
✓ Music (15GB)

Total: ~295GB
Free space: 1.7TB

Backup schedule:
- Full backup: Mỗi tháng
- Incremental: Mỗi tuần
- Cloud: Google Drive (100GB)

Lần backup tiếp theo: 22/11/2025''',
                'category': 'Cá nhân',
                'priority': 'Trung bình',
                'is_important': True,
                'is_completed': True,
                'due_date': None,
                'tags': ['personal', 'project']
            }
        ]
        
        notes_created = 0
        for note_data in sample_notes:
            try:
                note_id = str(uuid.uuid4())
                
                # Insert note
                cursor.execute("""
                    INSERT INTO notes 
                    (note_id, title, content, category_id, priority_id, 
                     is_completed, is_important, due_date, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    note_id,
                    note_data['title'],
                    note_data['content'],
                    categories[note_data['category']],
                    priorities[note_data['priority']],
                    note_data['is_completed'],
                    note_data['is_important'],
                    note_data.get('due_date'),
                    datetime.now() - timedelta(days=random.randint(0, 30)),
                    datetime.now()
                ))
                
                # Insert tags
                if 'tags' in note_data:
                    for tag_name in note_data['tags']:
                        if tag_name in tag_ids:
                            cursor.execute("""
                                INSERT INTO note_tags (note_id, tag_id)
                                VALUES (%s, %s)
                            """, (note_id, tag_ids[tag_name]))
                
                conn.commit()
                notes_created += 1
                print(f"   ✓ {note_data['title'][:50]}...")
                
            except Exception as e:
                print(f"   ✗ Lỗi: {e}")
        
        print(f"\n✅ Đã tạo {notes_created} notes mẫu")
        
        # Thống kê
        print("\n" + "=" * 70)
        print("📊 THỐNG KÊ DATABASE:")
        print("=" * 70)
        
        cursor.execute("SELECT COUNT(*) as count FROM notes")
        print(f"   • Tổng số notes: {cursor.fetchone()['count']}")
        
        cursor.execute("SELECT COUNT(*) as count FROM notes WHERE is_completed = TRUE")
        print(f"   • Notes đã hoàn thành: {cursor.fetchone()['count']}")
        
        cursor.execute("SELECT COUNT(*) as count FROM notes WHERE is_important = TRUE")
        print(f"   • Notes quan trọng: {cursor.fetchone()['count']}")
        
        cursor.execute("SELECT COUNT(*) as count FROM tags")
        print(f"   • Tổng số tags: {cursor.fetchone()['count']}")
        
        cursor.execute("SELECT COUNT(*) as count FROM note_tags")
        print(f"   • Tổng note-tag relations: {cursor.fetchone()['count']}")
        
        # Top categories
        print("\n📈 Notes theo category:")
        cursor.execute("""
            SELECT c.category_name, COUNT(n.note_id) as count
            FROM categories c
            LEFT JOIN notes n ON c.category_id = n.category_id
            GROUP BY c.category_id, c.category_name
            ORDER BY count DESC
        """)
        for row in cursor.fetchall():
            print(f"   • {row['category_name']}: {row['count']} notes")
        
        print("\n" + "=" * 70)
        print("✅ SEEDING HOÀN TẤT!")
        print("=" * 70)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")

if __name__ == "__main__":
    print("\n💡 Script này sẽ tạo dữ liệu mẫu cho database.")
    print("   Bao gồm: Notes, Tags, và quan hệ Note-Tags\n")
    
    response = input("Tiếp tục seeding? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        seed_database()
    else:
        print("❌ Đã hủy seeding.")
