# file: sound_manager.py

import pygame
import os
from typing import Dict, Optional

class SoundManager:
    #*Quản lý việc tải và phát các hiệu ứng âm thanh và nhạc nền.#*

    def __init__(self):
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_loaded = False 
        self._load_sounds()
        
    def _load_sounds(self):
        # Lấy thư mục gốc của dự án (Lùi 1 cấp từ vị trí file sound_manager.py)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        # Đường dẫn an toàn đến thư mục assets/sounds
        base_dir = os.path.join(project_root, "sounds")

        # Ánh xạ tên file âm thanh
        sound_files = {
            "move": "move.mp3",
            "eat_food": "eat_food.mp3",
            "eat_pie": "eat_magic.mp3",
            "teleport": "tele.mp3", 
            "game_over": "game_over.mp3",
            "win": "win.mp3",
        }

        # Tải nhạc nền (dùng pygame.mixer.music)
        music_path = os.path.join(base_dir, "background.mp3")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                self.music_loaded = True
            except pygame.error as e:
                print(f"Error loading music {music_path}: {e}")
        else:
            print(f"Warning: Music file not found at {music_path}")

        # Tải hiệu ứng âm thanh (dùng pygame.mixer.Sound)
        for name, filename in sound_files.items():
            path = os.path.join(base_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except pygame.error as e:
                    print(f"Error loading sound {filename}: {e}")
            else:
                print(f"Warning: Sound file not found: {path}")

    def play_sound(self, name: str, loops: int = 0):
        #*Phát hiệu ứng âm thanh đã tải.#*
        if name in self.sounds:
            self.sounds[name].play(loops)
            
    def play_music(self, volume: float = 0.5, loops: int = -1):
        #*Phát nhạc nền (loops=-1 là lặp vô hạn).#*
        if not self.music_loaded:
            return
        if pygame.mixer.music.get_busy():
            return
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(loops)

    def stop_music(self):
        #*Dừng nhạc nền.#*
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()