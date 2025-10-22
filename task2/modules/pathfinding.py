from itertools import groupby
from heapq import heappop, heappush
from collections import deque
from typing import Set, Dict, Tuple
from .game import Game, Pos, directions
  
class PathFinder:
  def __init__(self, src: Game):
    self.src = src
  
  #*-------------------------------
  #! HÀM HỖ TRỢ TÍNH HEURISIC (BFS)
  #*-------------------------------
  
  def _shortest_path_cost(self, start: Pos, end: Pos, 
                          walls: set[Pos], portals: list[Pos],powerup_turns: int
                          ,w: int, h: int)->int:
    if start == end:
      return 0
    queue = deque([(start, 0)])
    visited: Set[Pos] = {start}

    
    while queue:
      (x, y), cost = queue.popleft()
      for direction_name, (dx, dy) in directions.items():
        if direction_name == "STOP": continue
        nx, ny = x + dx, y + dy
        new_pos = (nx, ny)
        
        if new_pos == end:
          return cost + 1
        
        #* Kiểm tra Biên 
        if not (0 <= nx < w and 0 <= ny < h):
          continue
        
        #* Xử lý cổng tele
        if new_pos in portals:
          current_portal = new_pos
          #* Từ cổng hiện tại đến bất kì cổng nào cho chi phí là 1
          for target_portal in portals:
            if target_portal != current_portal and target_portal not in visited:
              visited.add(target_portal)
              queue.append((target_portal, cost + 1))
          visited.add(new_pos)
          continue
        
        #* Kiểm tra Tường
        if (new_pos in walls and powerup_turns ==0) or (new_pos in visited): 
          continue
        
        visited.add(new_pos)
        queue.append((new_pos, cost + 1))
        
    return float('inf') #* Nếu không thấy trả về chi phí vô hạn 
  
  #*-------------------------------
  #! HÀM HEURISTIC h(n)
  #*-------------------------------
  
  def estimate(self, game: Game) -> int:
    current_walls = game.walls
    current_portals = game.portals
    current_powerup_turns = game.powerup_turns    
    #* Nếu food đã được ăn hết => tìm exit
    if not game.food_points:
      cost = self._shortest_path_cost(game.player, game.exit_pos,
                                      current_walls,current_portals,current_powerup_turns,
                                      game.w, game.h)
      return cost if cost != float('inf') else 100000
    
    #* Nếu food chưa được ăn hết => tìm food gần nhất
    min_dist_to_food = float('inf')
        
    for food_pos in game.food_points:
      dist = self._shortest_path_cost(game.player, food_pos,
                                      current_walls, current_portals,current_powerup_turns,
                                      game.w, game.h)
      min_dist_to_food = min(min_dist_to_food, dist)
    
    return min_dist_to_food if min_dist_to_food != float('inf') else 100000
  
  #*-------------------------------
  #! THUẬT TOÁN A*
  #*-------------------------------
  
  def find(self) -> list[str]:
    #* frontier: (f_cost, g_cost, game_state)
    frontier = [(self.estimate(self.src), 0 ,hash(self.src),self.src)]
    g_cost_best: Dict[int, int] = {hash(self.src): 0}
    parent_map: Dict[int, Tuple[Game, str]] = {} #* Lưu trạng thái Game và hướng di chuyển: Cha của trạng Game hiện Tại
    
    while frontier:
      f_cost, g_cost,state_hash, game = heappop(frontier)
      
      if game.is_game_over() or g_cost > g_cost_best.get(state_hash, float('inf')):
        continue
      
      if game.is_winner():
        path = []
        current_hash = state_hash
        while current_hash != hash(self.src):
          parent_game, direction = parent_map[current_hash]
          path.append(direction)
          current_hash = hash(parent_game)
          
        return path[::-1]
      
      #* Lặp qua tất cả các action
      for direction, new_pos in game.get_moves().items():
        
        #* Get successor
        new_game = game.move_to(new_pos, direction)
        new_state_hash = hash(new_game)
        new_g_cost = g_cost + 1
        
        if new_game.is_game_over():
          continue
        
        #* Nếu chi phí mới tốt hơn chi phí cũ thì cập nhật lại
        if new_g_cost < g_cost_best.get(new_state_hash, float('inf')):
          g_cost_best[new_state_hash] = new_g_cost
          
          parent_map[new_state_hash] = (game, direction)
          
          new_h_cost = self.estimate(new_game)
          new_f_cost = new_g_cost + new_h_cost
          
          heappush(frontier, (new_f_cost, new_g_cost, new_state_hash, new_game))
          
    return [] # không tìm thấy đường
  
  def find_path_to(self, target: Pos)-> list[str]:
    src = self.src
    temp_game = Game(
        src.w, src.h, src.player,set(),
        set(), src.walls, target, src.ghost_states,
        src.powerup_turns, src.rotation_step, src.portals
    )
    temp_finder = PathFinder(temp_game)
    return temp_finder.find()
  
def find_multi_stage_path(game_src):
    full_path = []
    game = game_src
    
    finder_util = PathFinder(game) 
    
    while game.food_points:
        
        #* 1. Chuẩn bị các tham số
        current_walls = game.walls
        current_portals = game.portals

        min_cost = float('inf')
        target_pos = None
        
        #* 2. Tính toán chi phí BFS thực tế đến TẤT CẢ các mục tiêu
        for food_target in game.food_points: #* Dùng food_target để tránh nhầm lẫn
            #* Chi phí Tới FOOD trực tiếp
            cost_direct_to_food = finder_util._shortest_path_cost(
                game.player, food_target,
                current_walls, current_portals,game.powerup_turns,
                game.w, game.h
            )
            
            best_cost_for_this_food = cost_direct_to_food
            best_first_step = food_target #* Mặc định là đi thẳng tới Food
            
            #* Lặp qua tất cả Magic Pies để tìm đường tối ưu hơn
            for magic in game.magical_pies:
                cost_magic = finder_util._shortest_path_cost(
                    game.player, magic,
                    current_walls, current_portals, game.powerup_turns,
                    game.w, game.h
                )
                cost_food_after_eat_magic = finder_util._shortest_path_cost(
                    magic, food_target,
                    current_walls, current_portals, 5, #* Powerup = 5 khi đi từ magic
                    game.w, game.h
                )
                cost_via_magic = cost_magic + cost_food_after_eat_magic
                
                #* So sánh: (P -> F) vs (P -> M -> F)
                if cost_via_magic < best_cost_for_this_food:
                    best_cost_for_this_food = cost_via_magic
                    best_first_step = magic 
            
            if best_cost_for_this_food < min_cost:
                min_cost = best_cost_for_this_food
                target_pos = best_first_step 
        if target_pos is None or min_cost == float('inf'):
            print("Unable to find path to any target.")
            break
            
        #* 3. Tìm đường đi A* chính xác đến mục tiêu gần nhất đã chọn (Dùng find_path_to)
        finder_a_star = PathFinder(game)
        sub_path = finder_a_star.find_path_to(target_pos)
        
        if not sub_path:
            print(f"Error A*: Detailed route not found{target_pos}!")
            break
          
        #* 4. Thực hiện di chuyển từng bước
        for step in sub_path:
            next_pos = game.get_moves()[step]
            game = game.move_to(next_pos, step)
            full_path.append(step)
            
            
    #* 5. khi hết food, tìm đường đến exit
    #* 5.1. Tính chi phí đi thẳng đến Exit
    cost_direct_to_exit = finder_util._shortest_path_cost(
        game.player, game.exit_pos,
        game.walls, game.portals, game.powerup_turns,
        game.w, game.h
    )
    
    min_cost = cost_direct_to_exit
    final_target = game.exit_pos
    
    #* 5.2. Xem xét việc ăn Magic Pie (nếu còn)
    for magic in game.magical_pies:
        #* P -> M
        cost_p_to_m = finder_util._shortest_path_cost(
            game.player, magic,
            game.walls, game.portals, game.powerup_turns,
            game.w, game.h
        )
        #* M -> E
        cost_m_to_e = finder_util._shortest_path_cost(
            magic, game.exit_pos,
            game.walls, game.portals, 5, 
            game.w, game.h
        )
        cost_via_magic = cost_p_to_m + cost_m_to_e
        
        #* So sánh: (P -> E) vs (P -> M -> E)
        if cost_via_magic < min_cost:
            min_cost = cost_via_magic
            final_target = magic # Mục tiêu đầu tiên là Magic Pie
            
    #* 5.3. Tìm đường đi A* đến mục tiêu cuối cùng đã chọn
    if final_target == game.exit_pos:
        #* Đi thẳng đến Exit
        finder = PathFinder(game)
        exit_path = finder.find_path_to(game.exit_pos)
        full_path.extend(exit_path)
    else:
        #* Cần ăn Magic Pie trước
        finder_to_magic = PathFinder(game)
        path_to_magic = finder_to_magic.find_path_to(final_target)
        #* Thực hiện di chuyển đến Magic
        for step in path_to_magic:
            next_pos = game.get_moves()[step]
            game = game.move_to(next_pos, step)
            full_path.append(step)

        #* Sau khi ăn Magic, tìm đường đến Exit
        finder_to_exit = PathFinder(game)
        exit_path = finder_to_exit.find_path_to(game.exit_pos)
        full_path.extend(exit_path)
    
    return full_path

def compress_path(path: list[str]) -> str:
  #* Nén chuỗi hành động: ['NORTH', 'NORTH',...] -> 'NORTH1 EAST1'
  if not path:
    return ""
  
  compressed = []
  for key, group in groupby(path):
    count = len(list(group))
    if "TELE_P" in key:
      compressed.append(key)
    else:
      compressed.append(f"{key}-{count}")
      
  return ", ".join(compressed)
