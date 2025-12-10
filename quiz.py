import pygame

class QuizManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # --- CẤU HÌNH FONT CHỮ ---
        try:
            # Dùng font Arial in đậm cho rõ
            self.font_q = pygame.font.SysFont("Arial", 26, bold=True)
            self.font_a = pygame.font.SysFont("Arial", 22, bold=True)
        except:
            self.font_q = pygame.font.Font(None, 30)
            self.font_a = pygame.font.Font(None, 24)

        # --- LOAD VÀ CHỈNH ẢNH BẢNG (BOARD) ---
        # Load ảnh bảng đã tách nền
        self.board_img = pygame.image.load("Images/Board/board-removebg-preview.png").convert_alpha()
        
        # Thu nhỏ bảng cho vừa màn hình (khoảng 70% chiều ngang màn hình)
        target_w = int(screen_width * 0.7)
        scale_ratio = target_w / self.board_img.get_width()
        target_h = int(self.board_img.get_height() * scale_ratio)
        self.board_img = pygame.transform.scale(self.board_img, (target_w, target_h))
        
        # Đặt bảng ở giữa màn hình
        self.board_rect = self.board_img.get_rect(center=(screen_width//2, screen_height//2))

        # --- LOAD VÀ CHỈNH ẢNH NÚT (A, B, C, D) ---
        self.buttons = []
        labels = ["A", "B", "C", "D"]
        
        # Kích thước nút (bạn có thể chỉnh số này nếu nút to/nhỏ quá)
        btn_w, btn_h = 300, 60 
        
        # Vị trí nút đầu tiên (nằm dưới tâm bảng một chút)
        start_y = self.board_rect.centery - 10
        start_x = self.board_rect.centerx - btn_w // 2 # Căn giữa theo chiều ngang
        
        for i, label in enumerate(labels):
            # Load ảnh A.png, B.png...
            img = pygame.image.load(f"Images/Board/{label}.png").convert_alpha()
            img = pygame.transform.scale(img, (btn_w, btn_h))
            
            # Xếp các nút dọc xuống
            y = start_y + i * (btn_h + 15) # Cách nhau 15px
            rect = img.get_rect(topleft=(start_x, y))
            
            self.buttons.append({"img": img, "rect": rect, "label": label})

        self.current_question = None
        self.is_active = False # Biến kiểm tra xem có đang hiện bảng không

    def start_quiz(self, question_data):
        """Hàm kích hoạt bảng câu hỏi"""
        self.current_question = question_data
        self.is_active = True

    def draw(self, screen):
        """Vẽ toàn bộ giao diện giải đố"""
        if not self.is_active: return

        # 1. Làm tối màn hình game phía sau (hiệu ứng mờ)
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 2. Vẽ cái bảng
        screen.blit(self.board_img, self.board_rect)

        # 3. Vẽ câu hỏi
        if self.current_question:
            q_text = self.current_question["question"]
            # Render chữ màu Trắng, đặt ở phần trên của bảng
            text_surf = self.font_q.render(q_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(self.screen_width//2, self.board_rect.top + 130))
            screen.blit(text_surf, text_rect)

            # 4. Vẽ các nút và đáp án
            for i, btn in enumerate(self.buttons):
                # Vẽ ảnh nút A, B, C, D
                screen.blit(btn["img"], btn["rect"])
                
                # Vẽ chữ đáp án đè lên nút
                if i < len(self.current_question["options"]):
                    ans_text = self.current_question["options"][i]
                    # Chữ màu Đen cho dễ đọc trên nền vàng/cam
                    ans_surf = self.font_a.render(ans_text, True, (0, 0, 0))
                    
                    # Căn chữ nằm lệch sang phải icon bánh răng
                    ans_rect = ans_surf.get_rect(midleft=(btn["rect"].left + 70, btn["rect"].centery))
                    screen.blit(ans_surf, ans_rect)

    def handle_input(self, event):
        """Xử lý khi người chơi bấm chuột"""
        if not self.is_active: return None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, btn in enumerate(self.buttons):
                if btn["rect"].collidepoint(mouse_pos):
                    # Kiểm tra đáp án đúng sai
                    is_correct = (i == self.current_question["correct_index"])
                    self.is_active = False # Tắt bảng sau khi chọn
                    return is_correct 
        return None