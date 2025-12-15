import pygame

class ParallaxBackground:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.images = []
        
        # --- CẤU HÌNH HIỆU ỨNG NHÚNG NHẢY ---
        self.timer = 0
        self.interval = 180  
        self.y_offset = 0    
        self.target_y = 0    
        self.move_speed = 0.1 
        
        # [SỬA ĐỔI 1] Định nghĩa biên độ nhún tối đa để dùng cho việc tính toán
        self.max_bounce = 20 

        # Load 5 ảnh từ plx-1.png đến plx-5.png
        for i in range(1, 3):
            try:
                image_path = f"Images/parallax background/plx-{i}.png"
                image = pygame.image.load(image_path).convert_alpha()
                
                # [SỬA ĐỔI 2] Phóng to ảnh CAO HƠN màn hình một chút (bằng đúng độ nhún)
                # Chiều cao mới = màn hình + biên độ nhún
                new_height = screen_height + self.max_bounce 
                image = pygame.transform.scale(image, (screen_width, new_height))
                
                self.images.append(image)
                print(f"Loaded {image_path}")
            except Exception as e:
                print(f"Lỗi không tìm thấy ảnh {image_path}: {e}")

    def draw(self, screen):
        # 1. Cập nhật bộ đếm thời gian
        self.timer += 1
        
        # 2. Logic chuyển đổi trạng thái
        if self.timer >= self.interval:
            self.timer = 0 
            # Đổi mục tiêu: Nếu đang nhắm tới 0 thì đổi sang max_bounce (20)
            if self.target_y == 0:
                self.target_y = self.max_bounce
            else:
                self.target_y = 0
        
        # 3. Hiệu ứng di chuyển mượt mà (Interpolation)
        if self.y_offset < self.target_y:
            self.y_offset += self.move_speed
            if self.y_offset > self.target_y: 
                self.y_offset = self.target_y
                
        elif self.y_offset > self.target_y:
            self.y_offset -= self.move_speed
            if self.y_offset < self.target_y: 
                self.y_offset = self.target_y

        # 4. Vẽ các lớp ảnh
        for img in self.images:
            # [SỬA ĐỔI 3] Vẽ ảnh lùi lên trên một đoạn (trừ đi max_bounce)
            # Khi y_offset = 0 -> vẽ tại -20 (Che kín mép trên, dư mép dưới)
            # Khi y_offset = 20 -> vẽ tại 0 (Vừa khít mép trên, vừa khít mép dưới)
            draw_pos_y = self.y_offset - self.max_bounce
            
            screen.blit(img, (0, draw_pos_y))