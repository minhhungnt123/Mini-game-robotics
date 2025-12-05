import pygame

class ParallaxBackground:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.images = []
        
        # Load 5 ảnh từ plx-1.png đến plx-5.png
        for i in range(1, 6):
            try:
                # Đường dẫn ảnh
                image_path = f"Images/parallax background/plx-{i}.png"
                image = pygame.image.load(image_path).convert_alpha()
                
                # Phóng to ảnh cho vừa khít màn hình game
                image = pygame.transform.scale(image, (screen_width, screen_height))
                self.images.append(image)
                print(f"Loaded {image_path}")
            except Exception as e:
                print(f"Lỗi không tìm thấy ảnh {image_path}: {e}")

        # --- CẤU HÌNH HIỆU ỨNG NHÚNG NHẢY ---
        self.timer = 0
        self.interval = 180  # Thời gian chờ (số frame). 180 frames ~ 3 giây (nếu 60 FPS)
        self.y_offset = 0    # Vị trí y hiện tại
        self.target_y = 0    # Vị trí y muốn đến (0 hoặc 5)
        self.move_speed = 0.1 # Tốc độ di chuyển y (càng nhỏ càng mượt)

    def draw(self, screen):
        # 1. Cập nhật bộ đếm thời gian
        self.timer += 1
        
        # 2. Logic chuyển đổi trạng thái (cứ sau khoảng interval)
        if self.timer >= self.interval:
            self.timer = 0 # Reset đồng hồ
            
            # Đổi mục tiêu: Nếu đang nhắm tới 0 thì đổi sang 5, và ngược lại
            if self.target_y == 0:
                self.target_y = 20
            else:
                self.target_y = 0
        
        # 3. Hiệu ứng di chuyển mượt mà (Interpolation)
        # Nếu y hiện tại nhỏ hơn đích đến -> tăng y
        if self.y_offset < self.target_y:
            self.y_offset += self.move_speed
            if self.y_offset > self.target_y: 
                self.y_offset = self.target_y
                
        # Nếu y hiện tại lớn hơn đích đến -> giảm y
        elif self.y_offset > self.target_y:
            self.y_offset -= self.move_speed
            if self.y_offset < self.target_y: 
                self.y_offset = self.target_y

        # 4. Vẽ các lớp ảnh
        for img in self.images:
            # Vẽ ảnh tại vị trí x=0 (cố định) và y=y_offset (nhúng nhảy)
            screen.blit(img, (0, self.y_offset))