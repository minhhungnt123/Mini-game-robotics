import pygame

class QuizManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # --- CẤU HÌNH FONT CHỮ --- 
        try:
            # Font câu hỏi to hơn
            self.font_q = pygame.font.Font("Font\Mitr\Mitr-Medium.ttf", 24)
            # Font đáp án nhỏ hơn chút để vừa nút
            self.font_a = pygame.font.Font("Font\Mitr\Mitr-Medium.ttf", 16)
        except:
            self.font_q = pygame.font.SysFont("Arial", 30, bold=True)
            self.font_a = pygame.font.SysFont("Arial", 24, bold=True)

        # --- XỬ LÝ ẢNH BẢNG (BOARD) ---
        raw_board = pygame.image.load("Images/Board/board.png").convert_alpha()
        
        # Bảng chiếm 80% chiều rộng màn hình
        board_target_w = int(screen_width * 0.8)
        aspect_ratio = raw_board.get_height() / raw_board.get_width()
        board_target_h = int(board_target_w * aspect_ratio)
        
        # Scale ảnh bảng
        self.board_img = pygame.transform.smoothscale(raw_board, (board_target_w, board_target_h))
        self.board_rect = self.board_img.get_rect(center=(screen_width//2, screen_height//2))

        # --- XỬ LÝ CÁC NÚT (A, B, C, D) ---
        self.buttons = []
        labels = ["A", "B", "C", "D"]
        
        # Load 1 ảnh mẫu để lấy tỷ lệ nút
        temp_img = pygame.image.load("Images/Board/A.png").convert_alpha()
        btn_ratio = temp_img.get_height() / temp_img.get_width()
        
        # --- TÍNH TOÁN KÍCH THƯỚC VÀ VỊ TRÍ (GRID 2x2) ---
        # Chiều rộng nút = khoảng 38% chiều rộng bảng (để chừa khoảng trống ở giữa)
        btn_w = int(self.board_rect.width * 0.3)
        btn_h = int(btn_w * btn_ratio) # Chiều cao tự tính theo tỷ lệ ảnh gốc
        
        # Tọa độ gốc của bảng (Góc trên cùng bên trái của bảng)
        bx = self.board_rect.x
        by = self.board_rect.y
        bw = self.board_rect.width
        bh = self.board_rect.height

        # Tính vị trí cho 4 nút
        row1_y = by + int(bh * 0.46)
        row2_y = by + int(bh * 0.65)
        
        col1_x = bx + int(bw * 0.2)
        col2_x = bx + int(bw * 0.51)

        # Danh sách tọa độ cho [A, B, C, D]
        positions = [
            (col1_x, row1_y),
            (col2_x, row1_y),
            (col1_x, row2_y),
            (col2_x, row2_y)
        ]
        
        for i, label in enumerate(labels):
            img = pygame.image.load(f"Images/Board/{label}.png").convert_alpha()
            img = pygame.transform.smoothscale(img, (btn_w, btn_h))
            
            # Lấy tọa độ từ danh sách đã tính
            pos_x, pos_y = positions[i]
            
            rect = img.get_rect(topleft=(pos_x, pos_y))
            self.buttons.append({"img": img, "rect": rect, "label": label})

        self.current_question = None
        self.is_active = False

    def start_quiz(self, question_data):
        self.current_question = question_data
        self.is_active = True

    def draw(self, screen):
        if not self.is_active: return

        # 1. Làm tối màn hình
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 2. Vẽ bảng
        screen.blit(self.board_img, self.board_rect)

        if self.current_question:
            # --- VẼ CÂU HỎI ---
            # Vùng hiển thị câu hỏi (chiếm phần trên của bảng)
            q_text = self.current_question["question"]
            
            # Xử lý xuống dòng cho câu hỏi
            words = q_text.split(' ')
            lines = []
            curr_line = ""
            
            # Giới hạn chiều rộng text (khoảng 70% chiều rộng bảng)
            max_text_width = int(self.board_rect.width * 0.7)
            
            for word in words:
                test_line = curr_line + word + " "
                if self.font_q.size(test_line)[0] < max_text_width:
                    curr_line = test_line
                else:
                    lines.append(curr_line)
                    curr_line = word + " "
            lines.append(curr_line)

            # Vị trí bắt đầu vẽ câu hỏi (khoảng 22% từ đỉnh bảng xuống)
            start_text_y = self.board_rect.top + int(self.board_rect.height * 0.38)
            
            for i, line in enumerate(lines):
                text_surf = self.font_q.render(line, True, (255, 255, 255)) # Chữ trắng
                text_rect = text_surf.get_rect(center=(self.screen_width//2, start_text_y + i * 30))
                screen.blit(text_surf, text_rect)

            # --- VẼ NÚT VÀ ĐÁP ÁN ---
            for i, btn in enumerate(self.buttons):
                # Vẽ ảnh nút
                screen.blit(btn["img"], btn["rect"])
                
                # Vẽ chữ đáp án
                if i < len(self.current_question["options"]):
                    ans_text = self.current_question["options"][i]
                    
                    # 1. Tạo ảnh chữ gốc
                    ans_surf = self.font_a.render(ans_text, True, (255, 255, 255)) 
                    
                    # 2. Tính toán lề trái (Khoảng cách tránh icon A/B/C/D)
                    # Bạn có thể giảm 0.46 xuống 0.42 nếu muốn chữ lùi sang trái thêm chút nữa
                    padding_left = int(btn["rect"].width * 0.38) 
                    
                    # 3. --- LOGIC CHỐNG TRÀN (MỚI) ---
                    # Tính khoảng trống tối đa cho phép hiển thị chữ
                    # (Chiều rộng nút - Lề trái - 10px lề phải cho đẹp)
                    available_width = btn["rect"].width - padding_left - 1
                    
                    # Nếu chữ dài hơn khoảng trống cho phép, thì thu nhỏ nó lại
                    if ans_surf.get_width() > available_width:
                        scale_factor = available_width / ans_surf.get_width()
                        new_height = int(ans_surf.get_height() * scale_factor)
                        ans_surf = pygame.transform.smoothscale(ans_surf, (available_width, new_height))
                    # ---------------------------------

                    # 4. Vẽ chữ đã xử lý lên màn hình
                    text_x = btn["rect"].left + padding_left
                    text_y = btn["rect"].centery - (ans_surf.get_height() // 1.5) # Canh giữa theo chiều dọc
                    
                    screen.blit(ans_surf, (text_x, text_y))

    def handle_input(self, event):
        if not self.is_active: return None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, btn in enumerate(self.buttons):
                if btn["rect"].collidepoint(mouse_pos):
                    # Kiểm tra đúng sai
                    is_correct = (i == self.current_question["correct_index"])
                    self.is_active = False 
                    return is_correct 
        return None