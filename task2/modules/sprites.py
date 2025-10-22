import pygame
from typing import Dict, List, Optional
from .config import SPRITE_MAP, STATE_FILES 

class SpriteManager:
  def __init__(self, tile_size: int):
    self.tile_size = tile_size
    self.FOOD_SPRITE_SIZE = self.tile_size // 2
    self.FOOD_OFFSET = (self.tile_size - self.FOOD_SPRITE_SIZE) // 2 
    self.animation_frames: Dict[str, List[pygame.Surface]] = {}
    self.state_images: Dict[str, Optional[pygame.Surface]] = {}
    self._load_all_assets()
    self.player_base_size = self.tile_size
    self.player_powerup_size = int(self.tile_size * 1.5)
    
  def _load_all_assets(self):
    self._load_sprites()
    self._load_state_images()
    self.current_frame_index = 0
    self.frame_counter = 0
      
  def _load_sprites(self):
    for name, file_name in SPRITE_MAP.items():
      file_path = f"assets/{file_name}"
      try:
        image = pygame.image.load(file_path).convert_alpha()
        if name == "wall":
          scaled_image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
          self.animation_frames[name] = [scaled_image]
        else:
          frame_list = []
          # Giả sử các sprite animated có 4 frame nằm ngang
          frame_width = image.get_height() 
          target_size = self.FOOD_SPRITE_SIZE if name == "food" else self.tile_size
          num_frames = image.get_width()
          for i in range(int(num_frames/frame_width)): 
            frame = image.subsurface((i * frame_width, 0, frame_width, image.get_height()))
            scaled_frame = pygame.transform.scale(frame, (target_size, target_size))
            frame_list.append(scaled_frame)
          
          self.animation_frames[name] = frame_list
      except pygame.error:
        print(f"Lỗi: Không tìm thấy hoặc không tải được file '{file_path}'.")
        placeholder = pygame.Surface((self.tile_size, self.tile_size))
        placeholder.fill(pygame.Color("grey" if name == "wall" else "red"))
        self.animation_frames[name] = [placeholder]
      
  def _load_state_images(self):
    for state, file_name in STATE_FILES.items():
      try:
        self.state_images[state] = pygame.image.load(f"assets/{file_name}").convert_alpha()
      except pygame.error as e:
        print(f"Lỗi khi tải ảnh trạng thái '{file_name}': {e}.")
        self.state_images[state] = None
      
  def get_current_frame(self, name: str, is_powerup: bool = False) -> pygame.Surface:
        #*Trả về frame hiện tại của sprite theo tên, có thể scale nếu là player và có powerup.#*
        frames = self.animation_frames.get(name)
        if frames:
            # Wall chỉ có 1 frame
            if name == "wall":
                return frames[0]
            
            current_frame = frames[self.current_frame_index % len(frames)]
            
            if name == "player":
                target_size = self.player_powerup_size if is_powerup else self.player_base_size
                # Nếu kích thước cần thiết khác kích thước frame gốc, ta scale nó
                if target_size != current_frame.get_width():
                    return pygame.transform.scale(current_frame, (target_size, target_size))
            
            return current_frame
            
        # Trả về một placeholder nếu không tìm thấy
        placeholder = pygame.Surface((self.tile_size, self.tile_size))
        placeholder.fill(pygame.Color("black"))
        return placeholder
    
  def update_animation(self, animation_speed: int):
    #*Cập nhật chỉ số frame animation chung.#*
    self.frame_counter += 1
    if self.frame_counter >= animation_speed:
      self.frame_counter = 0
      self.current_frame_index = (self.current_frame_index + 1) % 4 # Giả sử 4 frame
  def get_rotation_angle(self, direction_name: str) -> int:
        #*Trả về góc quay (độ) cho sprite người chơi dựa trên hướng di chuyển.#*
        rotation_map = {
            "EAST": 0,
            "NORTH": 90,  # Quay 90 độ
            "WEST": 180,  # Quay 180 độ
            "SOUTH": 270, # Quay 270 độ
            "STOP": 0     # Giữ nguyên hướng khi dừng
        }
        base_direction = direction_name.split("_TELE_P")[0]
        return rotation_map.get(base_direction, 0)