import pygame
from .game import Game
# Import các HẰNG SỐ màu từ config.py để sử dụng (nên dùng chúng thay vì hardcode)
from .config import MODE_MANUAL_COLOR, MODE_AUTO_COLOR, POWERUP_COLOR

from typing import Tuple, Dict, Optional

pygame.font.init()

def draw_image_message(screen: pygame.Surface, state: str, window_size: Tuple[int, int], state_images: Dict[str, Optional[pygame.Surface]]):
    
    #*Vẽ ảnh trạng thái (Start/Win/Game Over/Paused) lên màn hình. (Giữ nguyên)*
    w, h = window_size
    
    if state in ["start", "game_over", "win", "paused"]:
        if state in state_images and state_images[state] is not None:
            image = state_images[state]
            
            # Tính toán scale và căn giữa 
            target_width = int(w * 0.7)
            scale_factor = target_width / image.get_width()
            target_height = int(image.get_height() * scale_factor)
            
            if target_height > h * 0.7:
                target_height = int(h * 0.7)
                scale_factor = target_height / image.get_height()
                target_width = int(image.get_width() * scale_factor)

            scaled_image = pygame.transform.smoothscale(image, (target_width, target_height))
            
            image_rect = scaled_image.get_rect(center=(w // 2, h // 2))
            screen.blit(scaled_image, image_rect)

def draw_hud(screen: pygame.Surface, game: Game, direction_name: str, is_manual_mode: bool, fps: int):
    #*Vẽ thanh HUD chuyên nghiệp (3 cột) ở phía trên màn hình. (Đã căn chỉnh)*
    
    w, h = screen.get_size()
    
    # --- Thiết lập Visual Style NÂNG CẤP ---
    HUD_HEIGHT = 70
    HUD_COLOR = pygame.Color("#1B263B")  # Nền Dark Blue/Navy
    LINE_COLOR = pygame.Color("#4A90E2")  # Đường phân cách sáng
    LABEL_COLOR = pygame.Color("#99AAB5")  # Màu ghi sáng hơn cho nhãn
    VALUE_COLOR = pygame.Color("#FFFFFF")  # Màu trắng tinh cho giá trị chính
    FPS_COLOR = pygame.Color("#2ECC71")  # Xanh lá cây sáng hơn cho FPS

    # 1. Vẽ thanh nền HUD và đường phân cách
    pygame.draw.rect(screen, HUD_COLOR, (0, 0, w, HUD_HEIGHT))
    pygame.draw.line(screen, LINE_COLOR, (0, HUD_HEIGHT), (w, HUD_HEIGHT), 2)

    # 2. Setup Fonts
    # Sử dụng font nhỏ hơn cho nhãn và lớn hơn cho giá trị để tạo sự phân cấp
    font_label = pygame.font.Font(None, 22)
    font_value = pygame.font.Font(None, 36)
    
    # 3. Tính toán vị trí cột và căn chỉnh
    
    # Vị trí cho 3 cột chính
    CENTER_COL_X = w // 2
    
    # Khoảng cách giữa nhãn và giá trị (chỉ dùng cho cột 3)
    LABEL_VALUE_GAP = 70 
    
    # Vị trí Y cho hàng trên và hàng dưới
    TOP_Y = 5
    MID_Y = 25 # [MỚI] Vị trí hàng giữa
    BOTTOM_Y = 45 # [MỚI] Vị trí hàng dưới cùng
    
    # X_POS cố định cho các nhãn (căn phải) và giá trị (căn phải) trong cột 3
    VALUE_RIGHT_X = w - 20 # Vị trí cố định cho giá trị (cách lề phải 20px)

    # MODE (Giá trị chính - căn trái)
    mode_text = "MODE: " + ("MANUAL" if is_manual_mode else "A* AUTO")
    mode_color = MODE_MANUAL_COLOR if is_manual_mode else MODE_AUTO_COLOR 
    mode_display = font_value.render(mode_text, True, mode_color)
    mode_display_rect = mode_display.get_rect(midleft=(20, HUD_HEIGHT // 2))
    screen.blit(mode_display, mode_display_rect)
    
    # DIRECTION
    dir_label = font_label.render("CURRENT DIRECTION", True, LABEL_COLOR)
    dir_value = font_value.render(direction_name, True, VALUE_COLOR)
    
    dir_label_rect = dir_label.get_rect(midtop=(CENTER_COL_X, TOP_Y))
    dir_value_rect = dir_value.get_rect(midtop=(CENTER_COL_X, MID_Y))
    
    screen.blit(dir_label, dir_label_rect)
    screen.blit(dir_value, dir_value_rect)
    
    # Cột 3: POWERUP - ROTATION - BƯỚC

    # POWERUP (TOP)
    powerup_color = POWERUP_COLOR if game.powerup_turns > 0 else LABEL_COLOR
    powerup_label = font_label.render("POWERUP:", True, LABEL_COLOR)
    powerup_value = font_value.render(f"{game.powerup_turns}", True, powerup_color)
    
    powerup_label_rect = powerup_label.get_rect(topright=(VALUE_RIGHT_X - LABEL_VALUE_GAP, TOP_Y + 5))
    powerup_value_rect = powerup_value.get_rect(topright=(VALUE_RIGHT_X, TOP_Y))
    
    screen.blit(powerup_label, powerup_label_rect)
    screen.blit(powerup_value, powerup_value_rect)

    # ROTATION (MID)
    rotation_color = pygame.Color("#3498DB") # Màu xanh dương
    rotation_label = font_label.render("ROTATION:", True, LABEL_COLOR)
    rotation_value = font_value.render(f"  {game.rotation_step}/30", True, rotation_color)
    
    rotation_label_rect = rotation_label.get_rect(topright=(VALUE_RIGHT_X - LABEL_VALUE_GAP, MID_Y + 5)) # Sử dụng MID_Y
    rotation_value_rect = rotation_value.get_rect(topright=(VALUE_RIGHT_X, MID_Y)) # Sử dụng MID_Y
    
    screen.blit(rotation_label, rotation_label_rect)
    screen.blit(rotation_value, rotation_value_rect)
    
    # BƯỚC (BOTTOM) - [THÊM]
    steps_color = pygame.Color("#FFD700") # Màu vàng Gold
    steps_label = font_label.render("STEP:", True, LABEL_COLOR)
    steps_value = font_value.render(f"  {game.steps}", True, steps_color)
    
    steps_label_rect = steps_label.get_rect(topright=(VALUE_RIGHT_X - LABEL_VALUE_GAP, BOTTOM_Y + 5)) # Sử dụng BOTTOM_Y
    steps_value_rect = steps_value.get_rect(topright=(VALUE_RIGHT_X, BOTTOM_Y)) # Sử dụng BOTTOM_Y
    
    screen.blit(steps_label, steps_label_rect)
    screen.blit(steps_value, steps_value_rect)

    # FPS ĐẶT RIÊNG Ở GÓC PHẢI DƯỚI HUD BAR
    fps_text = f"{int(fps)} FPS"
    fps_display = font_label.render(fps_text, True, FPS_COLOR)
    fps_rect = fps_display.get_rect(midtop=(CENTER_COL_X, BOTTOM_Y + 10)) # Căn giữa dưới
    screen.blit(fps_display, fps_rect)