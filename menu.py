import pygame
import os

# --- CẤU HÌNH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Menu:
    def __init__(self, width, height):
        self.width = width
        self.height = height  # <--- Biến chiều cao được lưu ở đây
        self.font = pygame.font.Font(None, 50)

        # ========== CẤU HÌNH KÍCH THƯỚC ==========
        self.TITLE_WIDTH_RATIO = 0.5
        self.BUTTON_SCALE_FACTOR = 0.5
        # =========================================
        
        # --- TẢI ẢNH TITLE ---
        title_path = os.path.join(BASE_DIR, "Images", "Menu", "menu_text.png")
        if os.path.exists(title_path):
            raw_title = pygame.image.load(title_path).convert_alpha()
            
            target_width = int(self.width * self.TITLE_WIDTH_RATIO)
            aspect_ratio = raw_title.get_height() / raw_title.get_width()
            target_height = int(target_width * aspect_ratio)

            self.title_img = pygame.transform.smoothscale(raw_title, (target_width, target_height))
        else:
            self.title_img = self.font.render("ROBOTICS GAME", True, (255, 255, 255))
        
        # --- TẢI ẢNH NÚT ---
        start_path = os.path.join(BASE_DIR, "Images", "Menu", "start_button.png")
        setting_path = os.path.join(BASE_DIR, "Images", "Menu", "setting_button.png")
        
        self.start_img = self._load_img_proportional(start_path, self.BUTTON_SCALE_FACTOR)
        self.setting_img = self._load_img_proportional(setting_path, self.BUTTON_SCALE_FACTOR)

        # --- TỌA ĐỘ ANIMATION ---
        self.state = "HIDDEN"
        self.anim_speed = 15

        # Title: Bay từ trên xuống
        # SỬA LỖI: Dùng self.height thay vì HEIGHT
        self.title_target_y = self.height * 0.05
        self.title_y = -self.title_img.get_height() - 50 
        self.title_x = (self.width - self.title_img.get_width()) // 2

        # Buttons: Bay từ dưới lên
        # SỬA LỖI: Dùng self.height thay vì HEIGHT
        self.btn_start_target_y = self.height * 0.65
        self.btn_setting_target_y = self.height * 0.8
        
        # SỬA LỖI: Dùng self.height thay vì HEIGHT
        self.btn_y_offset = self.height + 100 
        self.current_btn_offset = self.btn_y_offset

        # Rects cho buttons
        self.start_rect = self.start_img.get_rect(topleft=(0,0))
        self.setting_rect = self.setting_img.get_rect(topleft=(0,0))

    def _load_img_proportional(self, path, scale_factor):
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            new_w = int(img.get_width() * scale_factor)
            new_h = int(img.get_height() * scale_factor)
            return pygame.transform.smoothscale(img, (new_w, new_h))
        
        surf = pygame.Surface((int(200*scale_factor), int(80*scale_factor)))
        surf.fill((100, 100, 100))
        return surf

    def trigger_intro(self):
        self.state = "IN_TRANSITION"
        self.title_y = -self.title_img.get_height() - 50
        self.current_btn_offset = self.btn_y_offset

    def trigger_outro(self):
        self.state = "OUT_TRANSITION"

    def update(self):
        if self.state == "IN_TRANSITION":
            if self.title_y < self.title_target_y:
                self.title_y += self.anim_speed
            else:
                self.title_y = self.title_target_y
            
            if self.current_btn_offset > 0:
                self.current_btn_offset -= self.anim_speed
            else:
                self.current_btn_offset = 0
            
            if self.title_y >= self.title_target_y and self.current_btn_offset <= 0:
                self.title_y = self.title_target_y
                self.current_btn_offset = 0
                self.state = "ACTIVE"

        elif self.state == "OUT_TRANSITION":
            self.title_y -= self.anim_speed
            self.current_btn_offset += self.anim_speed

            if self.title_y < -self.title_img.get_height() - 50:
                return "DONE"

        return self.state

    def draw(self, screen):
        center_x = self.width // 2
        
        self.start_rect.center = (center_x, self.btn_start_target_y + self.current_btn_offset)
        self.setting_rect.center = (center_x, self.btn_setting_target_y + self.current_btn_offset)

        screen.blit(self.title_img, (self.title_x, self.title_y))
        screen.blit(self.start_img, self.start_rect)
        screen.blit(self.setting_img, self.setting_rect)

    def handle_input(self, event):
        if self.state == "ACTIVE" and event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_rect.collidepoint(event.pos):
                return "START"
            if self.setting_rect.collidepoint(event.pos):
                return "SETTING"
        return None