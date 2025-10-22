from typing import Optional, Set, List, Dict, Tuple

Pos = tuple[int,int] #* Định nghĩa kiểu dữ liệu cho vị trí (x, y)
GhostState = Tuple[Pos, Pos] #* Định nghĩa kiểu dữ liệu cho trạng thái Ghost: ((vị trí hiện tại), (hướng di chuyển))
#* Hướng di chuyển cơ bản
directions = {
  "WEST": (-1, 0),
  "EAST": (1, 0),
  "NORTH": (0, -1),
  "SOUTH": (0, 1),
  "STOP": (0, 0)
}

class Game:
  #! KHỞI TẠO TRẠNG THÁI GAME *
  __slots__ = (
        'w', 'h', 'player', 'food_points', 'magical_pies',
        'walls', 'exit_pos', 'ghost_states', 'powerup_turns',
        'rotation_step', 'portals','steps'
    )#* Sử dụng __slots__ để tối ưu hóa bộ nhớ và tăng tốc độ truy cập thuộc tính
  def __init__(self, w:int, h:int, player:Pos,
              food_points: set[Pos], magical_pies: set[Pos],
              walls: set[Pos], exit_pos: Pos,
              ghost_states: List[GhostState]=None,
              powerup_turns: int = 0,
              rotation_step: int = 0, portals: Optional[list[Pos]] = None,
              steps: int = 0): 
    self.w, self.h = w, h #* Kích thước chiều rộng và chiều cao của bản đồ
    self.player = player #* Vị trí hiện tại của Pacman (P)
    self.food_points = frozenset(food_points) #* Vị trí của các Food
    self.magical_pies = frozenset(magical_pies) #* Vị trí của các Bánh ma thuật
    self.walls = frozenset(walls) #* Tập hợp vị trí của các Bức tường
    self.exit_pos = exit_pos #* Vị trí của Lối ra
    self.powerup_turns = powerup_turns #* Số Power-up 
    self.rotation_step = rotation_step #* Bước đếm để xoay bản đồ 
    self.ghost_states = ghost_states if ghost_states is not None else [] #* Danh sách vị trí của Ghost
    #* Danh sách vị trí các cổng Teleport (mặc định là 4 góc)
    self.portals = portals if portals is not None else [(1, 1), (self.w - 2, 1), (self.w - 2, self.h - 2), (1, self.h - 2)]
    self.steps = steps #* Tổng số bước di chuyển của Pacman
    
  # ! HÀM TRỢ GIÚP XOAY BẢN ĐỒ  *
  
  #* Hàm xoay vị trí sang phải
  def _rotate_point(self, x: int, y:int, W: int, H: int) -> Pos:
    return H - 1 - y , x
  
  #* Hàm xoay toàn bộ trạng thái Game
  def _rotate_state(self) -> None:
    old_w, old_h = self.w, self.h
    
    #* Xoay vị trí pacman và exit
    self.player = self._rotate_point(*self.player, old_w, old_h)
    self.exit_pos = self._rotate_point(*self.exit_pos, old_w, old_h)
    
    #* Xoay vị trí vật phẩm và tường
    self.food_points = frozenset(self._rotate_point(*point, old_w, old_h) for point in self.food_points)
    self.magical_pies = frozenset(self._rotate_point(*point, old_w, old_h) for point in self.magical_pies)
    self.walls = frozenset(self._rotate_point(*point, old_w, old_h) for point in self.walls)
    self.portals = [self._rotate_point(*point, old_w, old_h) for point in self.portals]
    
    #* Xoay vị trí ghost
    self.ghost_states = [( self._rotate_point(x, y, old_w, old_h),(dx , dy)) for (x, y), (dx, dy) in self.ghost_states]
    
    #* Cập nhật kích thước
    self.w, self.h = old_h, old_w
    self.rotation_step = 0
  
  #!  HÀM CỐT LÕI CỦA GHOST    
  
  #* Tính toán trạng thái Ghost tiếp theo dựa trên vị trí và hướng hiện tại
  def _get_next_ghost_state(self, x:int, y:int, dx:int, dy:int)->GhostState:
    nx, ny = x + dx, y + dy
    #* Kiểm tra va chạm với tường
    if (nx, ny) in self.walls:
      return ((x, y), (-dx, -dy))
    return ((nx, ny), (dx, dy))
  
  #* Di chuyển tất cả các Ghost trong Game
  def _move_ghosts(self, current_ghost_states: List[GhostState])-> List[GhostState]:
    new_ghost_states = []
    for (pos, direction) in current_ghost_states:
      new_ghost_states.append(self._get_next_ghost_state(*pos,*direction))
    return new_ghost_states
  
  #! CÁC HÀM CỐT LÕI CỦA GAME *
  @classmethod
  def load_map(cls,map_str:str)-> "Game":
    lines = map_str.strip().splitlines()
    w,h = len(lines[0]), len(lines)
    
    #* Khởi tạo giá trị
    food_points, magical_pies, walls = set(), set(), set()
    player = None
    exit_pos = None
    ghost_states = []
    
    for y, row in enumerate(lines):
        for x, char in enumerate(row):
            pos = (x, y)
            match (char):
                case "P": player = pos
                case ".": food_points.add(pos)
                case "O": magical_pies.add(pos)
                case "E": exit_pos = pos
                case "%": walls.add(pos)
                case "G": ghost_states.append((pos, (1,0))) #* Mặc định di chuyển EAST
    if player is None or exit_pos is None:
      raise ValueError("Pacman location (P) or Exit location (E) not found!")
    return cls(w, h, player, food_points, magical_pies, walls, exit_pos, ghost_states=ghost_states)
  
  def is_game_over(self) -> bool:
    ghost_pos = {pos for pos, _ in self.ghost_states}
    return self.player in ghost_pos
  
  def is_winner(self) -> bool:
    return not self.food_points and self.player == self.exit_pos
  
  def get_moves(self) -> dict[str, Pos]:
    x, y = self.player
    moves = {}
    
    #* Lặp qua các action
    for direction, (dx, dy) in directions.items():
      nx, ny = x + dx, y + dy
      new_pos = nx, ny
      
      #* Kiểm tra vị trí hợp lệ ( trong biên và # tường)
      if (not (0 <= nx < self.w and 0 <= ny < self.h)) or (new_pos in self.walls and self.powerup_turns == 0):
          continue
      
      #* Di chuyển bình thường
      if direction == "STOP":
          moves["STOP"] = self.player
          continue
      
      #* 1. Di chuyển bình thường 
      moves[direction] = new_pos
      
      #* 2. Xử lý tele 
      if new_pos in self.portals:
        current_portal_index = self.portals.index(new_pos)
        for i in range(len(self.portals)):
          if i != current_portal_index:
            target_pos = self.portals[i]
            #* Tên hướng tele: DIRECTION_TELE_P{index+1}
            moves[f"{direction}_TELE_P{i+1}"] = target_pos
            
    return moves
  
  #* Tạo state mới với mỗi bước di chuyển của Pacman
  def move_to(self, new_pos: Pos, direction_name: str) -> "Game":
    
    pacman_old_pos = self.player
    pacman_new_pos = new_pos
    
    #*  1. Di chuyển Ghost  
    new_ghost_states = self._move_ghosts(self.ghost_states)
    
    new_powerup_turns = max(self.powerup_turns - 1, 0)
    new_walls = self.walls
    new_food_points = self.food_points
    new_magical_pies = self.magical_pies
    
    #*  2. KIỂM TRA VA CHẠM CHÉO (Crossing Collision)  
    is_crossing_collision = False
    
    for (g_old_pos, _), (g_new_pos, _) in zip(self.ghost_states, new_ghost_states):
      #* Va chạm chéo: P_new = G_old và G_new = P_old
      if pacman_new_pos == g_old_pos and g_new_pos == pacman_old_pos:
        is_crossing_collision = True
        break
            
    #* Nếu có va chạm chéo, trả về trạng thái Game Over
    if is_crossing_collision:
      game_over_state = Game(
          self.w, self.h, pacman_new_pos, new_food_points, new_magical_pies,
          new_walls, self.exit_pos, self.ghost_states, #* Truyền ghost cũ để is_over = true
          new_powerup_turns, 0, self.portals
      )
      return game_over_state
    
    #* Ăn tường tại new_pos
    if new_pos in self.walls and self.powerup_turns > 0:
      new_walls = self.walls - {new_pos}
      
    #* Ăn food tại new_pos
    if new_pos in self.food_points:
      new_food_points = self.food_points - {new_pos}
      
    #* Ăn magical pie tại new_pos
    if new_pos in self.magical_pies:
      new_magical_pies = self.magical_pies - {new_pos}
      new_powerup_turns = 5

    #* 4. Tạo Game State Mới  
    new_game = Game(
        self.w, self.h, new_pos, new_food_points, new_magical_pies,
        new_walls, self.exit_pos, new_ghost_states,
        new_powerup_turns, self.rotation_step, self.portals,self.steps+1
    )
    
    #* 5. Kiểm tra va chạm còn lại
    if new_game.is_game_over():
      new_game.rotation_step = 0
      return new_game
        
    #* 6. Xử lý Rotation  
    new_game.rotation_step += 1
    if new_game.rotation_step == 30:
      new_game._rotate_state()
      new_game.rotation_step = 0
    return new_game
  
  #! HASH VÀ EQUAL CHO A* VÀ FRONTIER
  
  def __hash__(self) -> int:
    return hash(( self.player, 
                  frozenset(self.food_points), 
                  frozenset(self.magical_pies), 
                  frozenset(self.walls), 
                  tuple(self.ghost_states),
                  self.powerup_turns,
                  self.rotation_step
                ))
    
  def __eq__(self, other: object) -> bool: 
    if not isinstance(other,Game):
      return False
    return (  self.player == other.player and
              self.food_points == other.food_points and
              self.magical_pies == other.magical_pies and
              self.walls == other.walls and
              self.ghost_states == other.ghost_states and
              self.powerup_turns == other.powerup_turns and
              self.rotation_step == other.rotation_step and 
              self.w == other.w and
              self.h == other.h
            )
  def __lt__(self, other: "Game") -> bool:
    return hash(self) < hash(other)