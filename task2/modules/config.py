import pygame
from typing import Dict

FPS = 120
TILE_SIZE = 64
ANIMATION_SPEED = 5
STEP_DELAY = 10 # Tốc độ bước đi A* mặc định

# Định nghĩa hướng di chuyển từ phím nhấn
KEY_TO_DIRECTION: Dict[int, str] = {
    pygame.K_UP: "NORTH", pygame.K_w: "NORTH",
    pygame.K_DOWN: "SOUTH", pygame.K_s: "SOUTH",
    pygame.K_LEFT: "WEST", pygame.K_a: "WEST",
    pygame.K_RIGHT: "EAST", pygame.K_d: "EAST",
    pygame.K_x : "STOP"
}

# Ánh xạ sprite
SPRITE_MAP = {
    "wall": "wall.png", "portal": "teleport.png",
    "player": "pacman.png", "food": "food.png",
    "magical_pie": "magic.png", "exit": "exit.png", "ghost": "ghost.png"
}

# Ánh xạ ảnh trạng thái
STATE_FILES = {"start": "start.png", "game_over": "over.png", "win": "win.png", "paused": "paused.png"}

# Màu sắc HUD
BAR_COLOR = (20, 20, 40)
MODE_MANUAL_COLOR = pygame.Color("#00E1FF")
MODE_AUTO_COLOR = pygame.Color("#00FF0D")
POWERUP_COLOR = pygame.Color("#FF4500")