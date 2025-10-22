import time
import sys
#*Cần import các lớp từ file module
from modules import Game, Renderer , find_multi_stage_path, compress_path


#*Kích thước bản đồ 
TITLE = "PACMAN GAME ASEAN"


def main():
  #* Tên file map mặc định
  map_file_name = "layouts/maze.txt"
  if len(sys.argv) > 1:
    map_file_name = sys.argv[1]
  try:
    with open(map_file_name, "r") as map_file:
      map_str = map_file.read()
      game_src = Game.load_map(map_str)
      print("\n    A* PATHFINDER MODE")
      print("===============================")
      print(f"Map: {map_file_name} ({game_src.w}x{game_src.h}) \n{map_str}")
      print("Computing path.")
      pathfind_time = time.time()
      path = find_multi_stage_path(game_src)

      pathfind_duration = time.time() - pathfind_time
      
      #* Sử dụng lại Game State khởi tạo để truyền vào Renderer
      game = Game.load_map(map_str)
      print(
        f"\n{'=' * 25}",
        f"\nPathfind duration: {pathfind_duration:.2f}s",
        f"\nSteps: {len(path) if path else 'N/A'}"
      )
      if path:
        print("RUN A* SUCCESSFULLY !")
        print("\nCompressed Path:", compress_path(path))
        #* Khởi tạo Renderer
        renderer = Renderer(game, map_str, TITLE, 1280, 720)
        
        #*Chạy game với đường đi A* đã tìm được
        print("===============================")
        print("       RUN SIMULATION")
        print("===============================")
        print("Use [SPACE] to start or pause")
        print("Use [M] to swap mode")
        print("Use [R] to Reset Game")
        print("Use [Q] to Exit Game")
        print("Use [WASD] or [ARROWS] to control the game\nUse [x] to stop")
        
        renderer.run(path)
      else:
        print("RUN A* DEFEATED !")
        print("\nCompressed Path:: No way found!")
      
  except FileNotFoundError:
      print(f"Error: Map file not found '{map_file_name}'.")
  except Exception as e:
      print(f"Error occurred during run: {e}")
      
if __name__ == "__main__":
  sys.path.append('.') 
  main()