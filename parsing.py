import math
import re

def parse_input_file(file_path):

    with open(file_path, 'r') as file:
        lines = file.readlines()

   
    grid_info = lines[0].strip().split(',')
    N = int(grid_info[0])  
    M = int(grid_info[1])  
    bend_penalty = int(grid_info[2]) 
    via_penalty = int(grid_info[3])  

    obstacles = []
    nets = {}

   
    for line in lines[1:]:
        line = line.strip()
        if line.startswith("OBS"):
           
            parts = line.split('(')[1].rstrip(')').split(',')
            layer, x, y = map(int, parts)
            obstacles.append((layer, x, y))
        elif line.startswith("net"):
           
            net_name = line.split()[0]
            pins = []
           
            pin_matches = re.findall(r'\(\d+,\s*\d+,\s*\d+\)', line)
            for pin in pin_matches:
                print(f"Raw pin: '{pin}'") 
                try:
                    
                    layer, x, y = map(int, pin.strip("()").split(','))
                    pins.append((layer, x, y))
                except ValueError as e:
                    print(f"Error parsing pin '{pin}': {e}")
                    continue
            nets[net_name] = pins

    return N, M, bend_penalty, via_penalty, obstacles, nets


def initialize_grid(N, M):
    
    grid = {}
    for x in range(N):
        for y in range(M):
            grid[(x, y)] = {'cost': 1.0, 'obstacle': False}  # 
    return grid


def set_obstacles(grid_M0, grid_M1, obstacles):
 
    for layer, x, y in obstacles:
        if layer == 0:
            grid_M0[(x, y)]['cost'] = math.inf
            grid_M0[(x, y)]['obstacle'] = True
        elif layer == 1:
            grid_M1[(x, y)]['cost'] = math.inf