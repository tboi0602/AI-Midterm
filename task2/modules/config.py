import pygame


#! HẰNG SỐ CƠ BẢN CỦA GAME *
FPS = 120 #* Số khung hình trên giây (Frames Per Second)
TILE_SIZE = 64 #* Kích thước của mỗi ô trên bản đồ (pixel)
ANIMATION_SPEED = 5 #* Tốc độ cập nhật frame animation (càng nhỏ càng nhanh)
STEP_DELAY = 10

#! ÁNH XẠ ĐIỀU KHIỂN *
#* Định nghĩa hướng di chuyển tương ứng với các phím nhấn
KEY_TO_DIRECTION = {
    pygame.K_UP: "NORTH", pygame.K_w: "NORTH",
    pygame.K_DOWN: "SOUTH", pygame.K_s: "SOUTH",
    pygame.K_LEFT: "WEST", pygame.K_a: "WEST",
    pygame.K_RIGHT: "EAST", pygame.K_d: "EAST",
    pygame.K_x : "STOP"
}

#! ÁNH XẠ TÀI NGUYÊN (SPRITE VÀ ẢNH TRẠNG THÁI) *
#* Ánh xạ tên logic của sprite với tên file hình ảnh tương ứng
SPRITE_MAP = {
    "wall": "wall.png", "portal": "teleport.png",
    "player": "pacman.png", "food": "food.png",
    "magical_pie": "magic.png", "exit": "exit.png", "ghost": "ghost.png"
}

#* Ánh xạ tên trạng thái game với tên file ảnh thông báo tương ứng
STATE_FILES = {"start": "start.png", "game_over": "over.png", "win": "win.png", "paused": "paused.png"}

#! HẰNG SỐ MÀU SẮC HUD *
BAR_COLOR = (20, 20, 40) #* Màu nền cho HUD 
MODE_MANUAL_COLOR = pygame.Color("#00E1FF") #* Màu hiển thị chế độ Thủ công
MODE_AUTO_COLOR = pygame.Color("#00FF0D") #* Màu hiển thị chế độ Tự động 
POWERUP_COLOR = pygame.Color("#FF4500") #* Màu hiển thị trạng thái Power-up