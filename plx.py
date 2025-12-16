import pygame

class ParallaxBackground:
    def __init__(self, screen_width, screen_height, image_files):
        self.width = screen_width
        self.height = screen_height
        self.images = []
        
        # --- CẤU HÌNH HIỆU ỨNG NHÚNG NHẢY ---
        self.timer = 0
        self.interval = 180  
        self.y_offset = 0    
        self.target_y = 0    
        self.move_speed = 0.1 
        self.max_bounce = 20 

        for img_path in image_files:
            try:
                image = pygame.image.load(img_path).convert_alpha()
                new_height = screen_height + self.max_bounce 
                image = pygame.transform.scale(image, (screen_width, new_height))
                
                self.images.append(image)
                print(f"Loaded {img_path}")
            except Exception as e:
                print(f"Lỗi không tìm thấy ảnh {img_path}: {e}")

    def draw(self, screen, alpha=255):
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0 
            if self.target_y == 0: self.target_y = self.max_bounce
            else: self.target_y = 0
        
        if self.y_offset < self.target_y:
            self.y_offset += self.move_speed
            if self.y_offset > self.target_y: self.y_offset = self.target_y     
        elif self.y_offset > self.target_y:
            self.y_offset -= self.move_speed
            if self.y_offset < self.target_y: self.y_offset = self.target_y

        for img in self.images:
            draw_pos_y = self.y_offset - self.max_bounce
            
            if alpha < 255:
                temp_img = img.copy()
                temp_img.set_alpha(alpha)
                screen.blit(temp_img, (0, draw_pos_y))
            else:
                screen.blit(img, (0, draw_pos_y))