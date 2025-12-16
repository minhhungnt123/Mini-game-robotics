import pygame
import os

class Menu:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        # --- CẤU HÌNH KÍCH THƯỚC CHO MENU CHÍNH ---
        self.menu_text_size = (750, 400) 
        self.btn_size = (350, 150)      
        
        # --- ASSETS CHO MENU CHÍNH ---
        try:
            # 1. Load và Scale Tiêu đề Game (Menu Text)
            img_text = pygame.image.load("Images/Menu/menu_text.png").convert_alpha()
            self.bg_image = pygame.transform.scale(img_text, self.menu_text_size)
            
            # 2. Load và Scale Nút Start
            img_start = pygame.image.load("Images/Menu/start_button.png").convert_alpha()
            self.btn_start_img = pygame.transform.scale(img_start, self.btn_size)
            
            # 3. Load và Scale Nút Setting
            img_setting = pygame.image.load("Images/Menu/setting_button.png").convert_alpha()
            self.btn_setting_img = pygame.transform.scale(img_setting, self.btn_size)
            
        except Exception as e:
            print(f"Menu Load Error: {e}")
            # Tạo hình tạm nếu lỗi load ảnh
            self.bg_image = pygame.Surface(self.menu_text_size)
            self.bg_image.fill((255, 255, 0)) # Màu vàng
            self.btn_start_img = pygame.Surface(self.btn_size)
            self.btn_start_img.fill((0, 255, 0)) # Màu xanh lá
            self.btn_setting_img = pygame.Surface(self.btn_size)
            self.btn_setting_img.fill((0, 0, 255)) # Màu xanh dương

        # Canh giữa các thành phần
        # Tiêu đề nằm trên
        self.bg_rect = self.bg_image.get_rect(center=(screen_width//2, screen_height//2 - 120))
        
        # Nút Start nằm giữa
        self.btn_start_rect = self.btn_start_img.get_rect(center=(screen_width//2, screen_height//2 + 100))
        
        # Nút Setting nằm dưới
        self.btn_setting_rect = self.btn_setting_img.get_rect(center=(screen_width//2, screen_height//2 + 200))

        # Animation states
        self.state = "INTRO" # INTRO, ACTIVE, OUTRO
        self.alpha = 0
        self.fade_speed = 5

    def trigger_intro(self):
        self.state = "INTRO"
        self.alpha = 0

    def trigger_outro(self):
        self.state = "OUTRO"

    def update(self):
        if self.state == "INTRO":
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.state = "ACTIVE"
                return "ACTIVE"
        
        elif self.state == "OUTRO":
            self.alpha -= self.fade_speed
            if self.alpha <= 0:
                self.alpha = 0
                return "DONE"
            
        return "RUNNING"

    def draw(self, screen):
        # Set alpha cho các thành phần
        self.bg_image.set_alpha(self.alpha)
        self.btn_start_img.set_alpha(self.alpha)
        self.btn_setting_img.set_alpha(self.alpha)

        screen.blit(self.bg_image, self.bg_rect)
        screen.blit(self.btn_start_img, self.btn_start_rect)
        screen.blit(self.btn_setting_img, self.btn_setting_rect)

    def handle_input(self, event):
        if self.state == "ACTIVE" and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Chuột trái
                if self.btn_start_rect.collidepoint(event.pos):
                    return "START"
                elif self.btn_setting_rect.collidepoint(event.pos):
                    return "SETTING"
        return None

# ========================================================
# CLASS QUẢN LÝ GAME OVER (MENU SAU TRÒ CHƠI)
# ========================================================
class GameOverMenu:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # ====================================================
        # [CẤU HÌNH KÍCH THƯỚC CHO GAME OVER TẠI ĐÂY]
        # ====================================================
        self.text_size = (750, 400) # (Rộng, Cao) chữ Game Over
        self.btn_size = (350, 150)   # (Rộng, Cao) nút Restart
        
        # Load Assets
        try:
            img_restart = pygame.image.load("Images/Menu/restart_button.png").convert_alpha()
            self.img_restart = pygame.transform.scale(img_restart, self.btn_size)
            
            img_text = pygame.image.load("Images/Menu/gameover_text.png").convert_alpha()
            self.img_text = pygame.transform.scale(img_text, self.text_size)
        except Exception as e:
            print(f"GameOverMenu Load Error: {e}")
            self.img_restart = pygame.Surface(self.btn_size)
            self.img_restart.fill((0, 255, 0))
            self.img_text = pygame.Surface(self.text_size)
            self.img_text.fill((255, 0, 0))

        # Tạo Rect (Căn giữa)
        self.rect_restart = self.img_restart.get_rect(center=(screen_width//2, screen_height//2 + 100))
        self.rect_text = self.img_text.get_rect(center=(screen_width//2, screen_height//2 - 150))
        
        # Biến quản lý hiệu ứng fade
        self.alpha = 0
        self.fade_speed = 3

    def reset(self):
        """Reset lại hiệu ứng fade để dùng cho lần chết sau"""
        self.alpha = 0

    def update(self):
        """Tăng độ mờ dần (Fade In)"""
        if self.alpha < 255:
            self.alpha += self.fade_speed
            if self.alpha > 255: self.alpha = 255
        return self.alpha # Trả về alpha để main.py dùng sync với background

    def draw(self, screen):
        """Vẽ Text và Button"""
        if self.alpha > 0:
            self.img_text.set_alpha(self.alpha)
            self.img_restart.set_alpha(self.alpha)
            
            screen.blit(self.img_text, self.rect_text)
            screen.blit(self.img_restart, self.rect_restart)

    def handle_input(self, event):
        """Xử lý click nút Restart"""
        # Chỉ nhận click khi đã hiện rõ (alpha >= 255)
        if self.alpha >= 255 and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Chuột trái
                if self.rect_restart.collidepoint(event.pos):
                    return "RESTART"
        return None