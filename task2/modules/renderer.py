import pygame
from .game import Game
from typing import List
#* Import các hằng số cấu hình cần thiết từ config
from .config import KEY_TO_DIRECTION, TILE_SIZE, FPS, ANIMATION_SPEED, STEP_DELAY
from .sprites import SpriteManager
from .sounds import SoundManager
from .hud import draw_hud, draw_image_message 
from .pathfinding import find_multi_stage_path 

class Renderer:
    def __init__(self, src: Game, initial_map_str: str, title: str, w: int, h: int, tile_size: int = TILE_SIZE, fps: int = FPS):
        #* Khởi tạo Pygame 
        pygame.init()
        pygame.font.init()
        #* Khởi tạo Mixer
        pygame.mixer.init()
        pygame.display.set_caption(title)
        
        self.src = src #! Đối tượng Game hiện tại, chứa trạng thái trò chơi
        self.initial_map_str = initial_map_str #* Chuỗi map ban đầu dùng để Reset game
        
        self.fps = fps 
        self.w, self.h = w, h
        self.tile_size = tile_size
        
        self.screen = pygame.display.set_mode((w, h))
        self.clock = pygame.time.Clock()
        
        self.sprite_manager = SpriteManager(self.tile_size) #* Quản lý hoạt ảnh
        self.sound_manager = SoundManager() #* Quản lý âm thanh 
        
        self.game_w, self.game_h = src.w, src.h #* Kích thước map thực tế (theo ô)
        self.is_running = True
        self.is_paused = True #! Trạng thái tạm dừng.
        self.current_state = "start" #* Trạng thái hiển thị (start, running, paused, game_over, win)
        self.player_direction_name = "EAST" #* Hướng hiện tại của người chơi dùng xoay hoạt ảnh
        
        self.STEP_DELAY = STEP_DELAY #* Số frame chờ giữa các bước đi 
        self.step_delay_counter = 0 #* Kiểm soát tốc độ di chuyển tự động
        self.reset_requested = False #* Báo hiệu yêu cầu reset game
        
        #* --- CHẾ ĐỘ CHƠI THỦ CÔNG & TELEPORT ---
        self.is_manual_mode = False #! True = Thủ công (WASD/Mũi tên), False = Tự động (A*)
        self.manual_move_requested = None #* Lệnh di chuyển thủ công (VD: "NORTH", "STOP", hoặc "EAST_TELE_P3")
        self.is_teleport_mode = False #! Trạng thái chờ người chơi chọn cổng đích
        self.tele_entry_direction = None #* Hướng đi vào cổng (VD: NORTH, EAST) - Dùng để tạo lệnh Teleport đích
        self.path = [] #* Đường đi A* (danh sách các hướng di chuyển)
        self.current_path_index = 0 #* Index hiện tại trong đường đi A*
        
        self._setup_surface()
        
    def _setup_surface(self):
        #* Thiết lập surface để vẽ bản đồ game. Surface này sẽ được scale và blit lên screen chính.
        surface_w = self.src.w * self.tile_size
        surface_h = self.src.h * self.tile_size
        self.surface = pygame.Surface((surface_w, surface_h)) #! Surface chứa bản đồ game
        
    def _calculate_auto_path(self):
        #* Tính toán đường đi A* và cập nhật self.path.
        print("Calculate the path A*")
        try:
            #* Gọi hàm tìm đường đi đa giai đoạn từ  pathfinding
            self.path = find_multi_stage_path(self.src) 
            print(f"Calculated A* path: {len(self.path)} step.")
        except Exception as e:
            #* Xử lý lỗi nếu không tìm được đường đi (ví dụ: đích bị chặn)
            print(f"Error in calculating path A*: {e}")
            self.path = []

    def handle_input(self):
        #* Xử lý tất cả các sự kiện đầu vào.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.is_running = False
                
                if event.key == pygame.K_r: 
                    self._reset_game()
                
                #* Không cho phép Tạm dừng (SPACE) hoặc Chuyển mode (M) khi đang chọn cổng
                if not self.is_teleport_mode:
                    if event.key == pygame.K_SPACE:
                        self._toggle_pause()
                    
                    if event.key == pygame.K_m:
                        self._toggle_mode()
                
                #* --- LOGIC CHỌN CỔNG TELEPORT (Chỉ kích hoạt khi đang ở chế độ chờ chọn cổng) ---
                if self.is_teleport_mode:
                    if pygame.K_1 <= event.key <= pygame.K_4:
                        target_index = event.key - pygame.K_0 #* Chuyển K_1 -> 1, K_4 -> 4
                        entry_direction = self.tele_entry_direction
                        
                        #* Tạo tên hướng tele: vd EAST_TELE_P3. Đây là lệnh di chuyển đặc biệt.
                        tele_direction = f"{entry_direction}_TELE_P{target_index}"
                        
                        self.manual_move_requested = tele_direction 
                        
                        #* Thoát chế độ chọn cổng và trở lại trạng thái đang chạy
                        self.is_teleport_mode = False
                        self.is_paused = False
                        self.current_state = "running"
                        self.tele_entry_direction = None
                        print(f"Player choose tele port number {target_index}.")
                        
                elif self.is_manual_mode and not self.is_paused:
                    #* Di chuyển thủ công (W, A, S, D, Mũi tên) hoặc Dừng (X)
                    if event.key in KEY_TO_DIRECTION:
                        #* Lưu hướng di chuyển, sẽ được xử lý trong vòng lặp run()
                        self.manual_move_requested = KEY_TO_DIRECTION[event.key]

    def _reset_game(self):
        #* Thiết lập lại game về trạng thái ban đầu.
        #* Tải lại game object từ chuỗi map ban đầu
        self.src = Game.load_map(self.initial_map_str)
        self.game_w, self.game_h = self.src.w, self.src.h 
        self.is_paused = True
        self.current_state = "start"
        self.step_delay_counter = 0
        self.reset_requested = True
        self.manual_move_requested = None
        self.is_teleport_mode = False
        self.tele_entry_direction = None
        self.current_path_index = 0
        self.path = [] 
        #* Nếu đang ở chế độ Tự động, cần phải tính toán lại đường đi sau khi reset
        if not self.is_manual_mode:
            self._calculate_auto_path()
        
    def _toggle_pause(self):
        #* Chuyển đổi trạng thái Tạm dừng.
        if self.current_state not in ["game_over", "win"] and not self.is_teleport_mode:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.current_state = "paused"
            elif self.current_state in ["start", "paused"]: 
                self.current_state = "running" #* Chỉ chuyển sang "running" khi tiếp tục chơi
    
    def _toggle_mode(self):
        #* Chuyển đổi giữa chế độ thủ công và tự động (A*).
        if self.current_state not in ["game_over", "win"] and not self.is_teleport_mode:
            self.is_manual_mode = not self.is_manual_mode
            self.is_paused = True #* Tạm dừng khi chuyển mode để người chơi chuẩn bị
            self.current_state = "paused"
            
            #* Reset các trạng thái liên quan đến di chuyển
            self.manual_move_requested = None
            self.is_teleport_mode = False
            self.tele_entry_direction = None
            self.current_path_index = 0
            
            if not self.is_manual_mode:
                #* Gọi hàm hỗ trợ để tính toán lại đường đi cho chế độ Tự động
                self._calculate_auto_path() 

    def _draw_entities(self, game: Game):
        #* Vẽ các thực thể (map, player, food, ghost, exit) lên surface.
        #* Vẽ các vật phẩm/cổng/tường - Vẽ theo tọa độ ô (x, y)
        for y in range(game.h):
            for x in range(game.w):
                pos = (x, y)
                blit_x, blit_y = x * self.tile_size, y * self.tile_size
                
                #* Vẽ tường (wall)
                if pos in game.walls:
                    self.surface.blit(self.sprite_manager.get_current_frame("wall"), (blit_x, blit_y))
                #* Vẽ cổng (portal)
                elif pos in game.portals:
                    self.surface.blit(self.sprite_manager.get_current_frame("portal"), (blit_x, blit_y))
                    
                #* Vẽ thức ăn và bánh ma thuật (thức ăn được căn giữa ô bằng offset)
                if pos in game.food_points:
                    food_frame = self.sprite_manager.get_current_frame("food")
                    self.surface.blit(food_frame, (blit_x + self.sprite_manager.FOOD_OFFSET, blit_y + self.sprite_manager.FOOD_OFFSET))
                elif pos in game.magical_pies:
                    magic_frame = self.sprite_manager.get_current_frame("magical_pie")
                    self.surface.blit(magic_frame, (blit_x , blit_y ))
        
        #* Vẽ Lối ra
        if game.exit_pos:
            self.surface.blit(self.sprite_manager.get_current_frame("exit"), (game.exit_pos[0] * self.tile_size, game.exit_pos[1] * self.tile_size))
            
        #* Vẽ Ghosts
        for ghost_current_pos, ghost_prev_pos in game.ghost_states:
            g_blit_x, g_blit_y = ghost_current_pos[0] * self.tile_size, ghost_current_pos[1] * self.tile_size
            self.surface.blit(self.sprite_manager.get_current_frame("ghost"), (g_blit_x, g_blit_y))
            
        #* Vẽ Player 
        if game.player:
            is_powerup_active = game.powerup_turns > 0 #* Kiểm tra trạng thái Power-up
            #* Lấy frame người chơi (có thể thay đổi nếu Power-up)
            player_frame = self.sprite_manager.get_current_frame("player", is_powerup=is_powerup_active) 
            #* Xoay sprite dựa trên hướng di chuyển cuối cùng
            rotated_player = pygame.transform.rotate(player_frame, self.sprite_manager.get_rotation_angle(self.player_direction_name))
            new_size = player_frame.get_width() 
            offset = (self.tile_size - new_size) // 2 
            #* Tính toán vị trí vẽ (căn giữa)
            p_blit_x, p_blit_y = game.player[0] * self.tile_size + offset, game.player[1] * self.tile_size + offset
            self.surface.blit(rotated_player, (p_blit_x, p_blit_y))

    def render(self, game: Game):
        #* Vẽ toàn bộ khung hình, bao gồm map, HUD và thông báo trạng thái.
        self.screen.fill(pygame.Color("#01052B"))
        self.surface.fill(pygame.Color("#010647"))
        
        self.sprite_manager.update_animation(ANIMATION_SPEED) #* Cập nhật frame hoạt ảnh cho các sprite
        
        self._draw_entities(game) #* Vẽ bản đồ và thực thể lên self.surface
        
        #* HIỂN THỊ MAP (SCALE VÀ CĂN GIỮA)
        rotated_surface = self.surface
        surface_w_orig, surface_h_orig = rotated_surface.get_size()
        #* Tính toán tỷ lệ scale để map vừa với màn hình (trừ phần HUD)
        scale_factor = min(self.w / surface_w_orig, (self.h - 70) / surface_h_orig) #! Trừ 70px cho HUD
        scaled_surface_w = int(surface_w_orig * scale_factor)
        scaled_surface_h = int(surface_h_orig * scale_factor)
        scaled_surface = pygame.transform.smoothscale(rotated_surface, (scaled_surface_w, scaled_surface_h))
        
        #* Tính toán vị trí căn giữa (có tính đến phần HUD)
        blit_x = (self.w - scaled_surface_w) // 2
        blit_y =70 + (self.h - 70 - scaled_surface_h) // 2 #* Bắt đầu vẽ từ 70px (dưới HUD)
        
        self.screen.blit(scaled_surface, (blit_x, blit_y))
        
        #* VẼ HUD & TRẠNG THÁI
        #* Hiển thị điểm, turn powerup, mode chơi, FPS
        draw_hud(self.screen, game, self.player_direction_name, self.is_manual_mode, self.clock.get_fps())
        
        #* Hiển thị thông báo chọn cổng nếu đang trong chế độ Teleport
        if self.is_teleport_mode:
            position = {(1,1): "TOP-LEFT",
                        (game.w-2,1): "TOP-RIGHT",
                        (game.w-2,game.h-2): "BOTTON-RIGHT",
                        (1,game.h-2): "BOTTON-LEFT"}
            
            TEXT_COLOR = pygame.Color("#FF8800")
            SHADOW_COLOR = pygame.Color("#FFFFFF") 
            SHADOW_OFFSET = 2 
            y_start = self.h // 3
            spacing = 80 
            for i, pos in enumerate(game.portals):
                current_y = y_start + i * spacing
                font = pygame.font.Font(None, 60)
                shadow_text = font.render(f"GATE: {i+1} {position[pos]}", True, SHADOW_COLOR)
                shadow_rect = shadow_text.get_rect(center=(self.w // 2, current_y)) 
                shadow_rect.x += SHADOW_OFFSET
                shadow_rect.y += SHADOW_OFFSET
                self.screen.blit(shadow_text, shadow_rect)
                text = font.render(f"GATE: {i+1} {position[pos]}", True, TEXT_COLOR)
                text_rect = text.get_rect(center=(self.w // 2, current_y)) 
                self.screen.blit(text, text_rect)
        else:
            #* Chỉ hiển thị thông báo trạng thái game (Start/Paused/Win/Over) khi không chọn cổng
            draw_image_message(self.screen, self.current_state, (self.w, self.h), self.sprite_manager.state_images)
        
        pygame.display.flip() #* Cập nhật toàn bộ màn hình

    def run(self, initial_path: List[str]):
        #* Vòng lặp chính của game
        game = self.src 
        self.path = initial_path 
        self.current_path_index = 0
        self.sound_manager.play_music()
        
        while self.is_running:
            self.clock.tick(self.fps)
            self.handle_input()
            
            #* Xử lý reset sau khi đã thực hiện _reset_game()
            if self.reset_requested:
                self.current_path_index = 0
                self.reset_requested = False
                game = self.src #! Gán lại game object mới sau khi reset
            
            self.render(game) #! Luôn vẽ hình dù đang tạm dừng hay đang chạy
            
            #* Chạy game khi không ở trạng thái pause game, over, win, và chọn cổng tele
            if self.current_state not in ["game_over", "win"] and not self.is_paused and not self.is_teleport_mode:
                self.sound_manager.play_music() 
                
                if self.is_manual_mode:
                    #* --- MANUAL MODE LOGIC ---
                    if self.manual_move_requested is not None:
                        direction_name = self.manual_move_requested
                        
                        #* 1. Thực hiện bước di chuyển
                        self._execute_move(game, direction_name)
                        game = self.src #* Cập nhật game object
                        self._check_game_state()
                        
                        #* 2. Xử lý sau di chuyển: Kiểm tra nếu người chơi vừa vào cổng
                        if "_TELE_P" not in direction_name:
                            #* Nếu người chơi đứng tại cổng và bước di chuyển không phải là STOP
                            if self.src.player in self.src.portals and direction_name != "STOP":
                                #! Kích hoạt chế độ chọn cổng và tạm dừng game
                                self.is_teleport_mode = True
                                self.is_paused = True
                                self.current_state = "paused" 
                                self.tele_entry_direction = direction_name #* Lưu hướng đi vào cổng
                                print("Entered the gate. Waiting for destination gate selection.")
                                
                        #* Reset request sau khi hoàn tất di chuyển
                        self.manual_move_requested = None
                        
                else:
                    #* --- AUTO MODE LOGIC ---
                    self.step_delay_counter += 1
                    
                    if self.step_delay_counter >= self.STEP_DELAY:
                        self.step_delay_counter = 0 
                        
                        if self.current_path_index < len(self.path):
                            direction_name = self.path[self.current_path_index] #* Lấy hướng tiếp theo từ đường đi A*
                            self.current_path_index += 1
                            
                            self._execute_move(game, direction_name)
                            game = self.src 
                            
                            self._check_game_state()
                            
                        elif self.current_path_index >= len(self.path) and self.current_state == "running":
                            #* Dừng game khi hết đường đi A*
                            self.is_paused = True
                            self.current_state = "paused" 
                
            elif self.is_paused or self.is_teleport_mode:
                self.sound_manager.stop_music()
                
        pygame.quit() 
    
    #! Thực hiện bước di chuyển và cập nhật trạng thái Renderer.
    def _execute_move(self, game: Game, direction_name: str):
        
        moves = game.get_moves()
        #* Lấy hướng cơ bản (NORTH, EAST,...) từ hướng tele (NORTH_TELE_P1)
        base_direction = direction_name.split("_TELE_P")[0]
        
        #*  XỬ LÝ TRƯỜNG HỢP DI CHUYỂN TELEPORT ---
        next_pos = None
        if "_TELE_P" in direction_name:
            target_index = int(direction_name.split("_TELE_P")[1])
            
            #* Tìm vị trí cổng đích (portal) trong game.portals
            next_pos = game.portals[target_index - 1] # Vị trí đích của Teleport
            
        #* --- LOGIC DI CHUYỂN BÌNH THƯỜNG / STOP ---
        elif base_direction == "STOP":
            next_pos = game.player #* Giữ nguyên vị trí
        elif direction_name in moves:
            #* Lấy vị trí đích cho di chuyển thường
            next_pos = moves[direction_name]
        else:
            #* Nếu hướng đi không hợp lệ thi báo lloix
            print(f"Error: Movement Direction '{direction_name}' invalid.")
            return

        if next_pos is None:
            #* Trường hợp lỗi logic không xác định được vị trí tiếp theo
            print(f"Error: No target location found for direction '{direction_name}'.")
            return
        
        #* Chỉ cập nhật hướng sprite nếu không phải lệnh STOP
        if base_direction != "STOP":
            self.player_direction_name = base_direction 
            self.sound_manager.play_sound("move")
        
        #* Lấy trạng thái game mới sau khi di chuyển (hàm game.move_to() thực hiện tất cả logic game)
        new_game_state = game.move_to(next_pos, direction_name) 

        #* Xử lý âm thanh ăn vật phẩm/teleport 
        if "_TELE_P" in direction_name:
            self.sound_manager.play_sound("teleport")
        else:
            #* Xử lý âm thanh ăn vật phẩm cho di chuyển thường
            old_food_count = len(game.food_points) + len(game.magical_pies)
            new_food_count = len(new_game_state.food_points) + len(new_game_state.magical_pies)
            
            if new_food_count < old_food_count:
                #* Kiểm tra nếu Power-up mới được kích hoạt (hoặc đang ở turn đầu tiên)
                if new_game_state.powerup_turns > game.powerup_turns or new_game_state.powerup_turns == 5:
                    self.sound_manager.play_sound("eat_pie")
                else:
                    self.sound_manager.play_sound("eat_food")
            
        #* --- Cập nhật trạng thái Game---
        self.src = new_game_state
        
        #*Cập nhật lại Renderer nếu map thay đổi (ví dụ: Xouay map)
        if self.src.w != self.game_w or self.src.h != self.game_h:
            
            #* Cập nhật kích thước mới cho Renderer
            self.game_w = self.src.w 
            self.game_h = self.src.h 
            
            #* Setup lại surface để vẽ lại map đúng kích cỡ
            self._setup_surface()
            
    def _check_game_state(self):
        #* Kiểm tra và cập nhật trạng thái game (Win/Game Over).
        game = self.src
        
        if game.is_game_over():
            self._set_state("game_over", "game_over")
            
        elif game.is_winner():
            self._set_state("win", "win")
            
    def _set_state(self, state_name, sound_name):
        #* Hàm phụ trợ để xử lý trạng thái cuối cùng (thắng/thua)
        self.is_paused = True
        self.current_state = state_name
        self.sound_manager.stop_music()
        self.sound_manager.play_sound(sound_name)