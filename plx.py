import pygame

class ParallaxBackground:
    # [SỬA ĐỔI 1] Nhận danh sách file ảnh (image_files) thay vì load cố định
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

        # [SỬA ĐỔI 2] Load ảnh từ danh sách truyền vào
        for img_path in image_files:
            try:
                image = pygame.image.load(img_path).convert_alpha()
                
                # Phóng to ảnh CAO HƠN màn hình (logic cũ)
                new_height = screen_height + self.max_bounce 
                image = pygame.transform.scale(image, (screen_width, new_height))
                
                self.images.append(image)
                print(f"Loaded {img_path}")
            except Exception as e:
                print(f"Lỗi không tìm thấy ảnh {img_path}: {e}")

    # [SỬA ĐỔI 3] Thêm tham số alpha để làm mờ
    def draw(self, screen, alpha=255):
        # 1. Logic cập nhật (giữ nguyên)
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0 
            if self.target_y == 0: self.target_y = self.max_bounce
            else: self.target_y = 0
        
        # Interpolation
        if self.y_offset < self.target_y:
            self.y_offset += self.move_speed
            if self.y_offset > self.target_y: self.y_offset = self.target_y     
        elif self.y_offset > self.target_y:
            self.y_offset -= self.move_speed
            if self.y_offset < self.target_y: self.y_offset = self.target_y

        # 2. Vẽ ảnh với độ trong suốt
        for img in self.images:
            draw_pos_y = self.y_offset - self.max_bounce
            
            if alpha < 255:
                # Nếu cần làm mờ: Tạo bản sao tạm, set alpha rồi vẽ
                # Lưu ý: Cách này hơi nặng nếu chạy liên tục trên máy yếu, 
                # nhưng với game 2D đơn giản thì ổn.
                temp_img = img.copy()
                temp_img.set_alpha(alpha)
                screen.blit(temp_img, (0, draw_pos_y))
            else:
                # Vẽ bình thường (tối ưu hơn)
                screen.blit(img, (0, draw_pos_y))