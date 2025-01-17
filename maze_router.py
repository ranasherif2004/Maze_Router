# -*- coding: utf-8 -*-
"""maze_router.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1i9xBgZWnBvSWxjw0RPvHdtZb0bhoPFsr
"""

import numpy as np
from queue import Queue
from typing import List, Tuple, Dict

class LeeRouter:
    def __init__(self, width: int, height: int, bend_penalty: int, via_penalty: int):

        self.width = width
        self.height = height
        self.bend_penalty = bend_penalty
        self.via_penalty = via_penalty

        self.layers = [
            np.zeros((height, width), dtype=int),
            np.zeros((height, width), dtype=int)
        ]

        self.routed_nets: Dict[str, Tuple[List[Tuple[int, int, int]], float]] = {}

    def add_obstacle(self, layer: int, x: int, y: int):

        if 0 <= y < self.height and 0 <= x < self.width:
            self.layers[layer][y, x] = -1

    def route_net(self, net_name: str, pins: List[Tuple[int, int, int]]) -> Tuple[List[Tuple[int, int, int]], float]:

        if len(pins) < 2:
            raise ValueError("Net must have at least two pins")

        adjusted_pins = []
        for layer, x, y in pins:
            x = max(0, min(x, self.width - 1))
            y = max(0, min(y, self.height - 1))
            adjusted_pins.append((layer, x, y))

        full_path = []
        total_cost = 0.0

        for i in range(len(adjusted_pins) - 1):
            start_layer, start_x, start_y = adjusted_pins[i]
            end_layer, end_x, end_y = adjusted_pins[i+1]

            path, cost = self._lee_route(
                start_layer, start_x, start_y,
                end_layer, end_x, end_y
            )
            full_path.extend(path[1:] if full_path else path)
            total_cost += cost

        self.routed_nets[net_name] = (full_path, total_cost)
        return full_path, total_cost

    def _lee_route(self, start_layer: int, start_x: int, start_y: int,
                   end_layer: int, end_x: int, end_y: int) -> Tuple[List[Tuple[int, int, int]], float]:

        directions = [
            (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1)
        ]

        wave_grid = [np.full((self.height, self.width), np.inf) for i in range(2)]

        prev_direction_grid = [
            np.full((self.height, self.width), -1, dtype=int) for i in range(2)
        ]

        wave_grid[start_layer][start_y, start_x] = 0
        prev_direction_grid[start_layer][start_y, start_x] = -1

        queue = Queue()
        queue.put((start_layer, start_x, start_y, -1))

        visited = set()

        while not queue.empty():
            curr_layer, curr_x, curr_y, prev_dir = queue.get()

            if curr_layer == end_layer and curr_x == end_x and curr_y == end_y:
                break

            if (curr_layer, curr_x, curr_y) in visited:
                continue
            visited.add((curr_layer, curr_x, curr_y))

            for dir_idx, (dx, dy, dlayer) in enumerate(directions):
                new_layer = curr_layer + dlayer
                new_x, new_y = curr_x + dx, curr_y + dy

                if (0 <= new_layer < len(self.layers) and
                    0 <= new_x < self.width and
                    0 <= new_y < self.height and
                    self.layers[new_layer if dlayer != 0 else curr_layer][new_y, new_x] != -1):

                    cost_increment = 1

                    if dlayer == 0 and prev_dir != -1:
                        prev_dx, prev_dy, _ = directions[prev_dir]
                        if (prev_dx != 0 and dy != 0) or (prev_dy != 0 and dx != 0):
                            cost_increment += self.bend_penalty

                    if dlayer != 0:
                        cost_increment += self.via_penalty

                    new_cost = wave_grid[curr_layer][curr_y, curr_x] + cost_increment

                    if new_cost < wave_grid[new_layer if dlayer != 0 else curr_layer][new_y, new_x]:
                        wave_grid[new_layer if dlayer != 0 else curr_layer][new_y, new_x] = new_cost
                        prev_direction_grid[new_layer if dlayer != 0 else curr_layer][new_y, new_x] = dir_idx
                        queue.put((new_layer if dlayer != 0 else curr_layer, new_x, new_y, dir_idx))

        final_cost = wave_grid[end_layer][end_y, end_x]
        if np.isinf(final_cost):
            raise ValueError("No valid path found")

        path = [(end_layer, end_x, end_y)]
        curr_layer, curr_x, curr_y = end_layer, end_x, end_y

        while not (curr_layer == start_layer and curr_x == start_x and curr_y == start_y):
            best_prev = None
            min_cost = np.inf

            for dx, dy, dlayer in directions:
                prev_layer = curr_layer - dlayer
                prev_x, prev_y = curr_x - dx, curr_y - dy

                if (0 <= prev_layer < len(self.layers) and
                    0 <= prev_x < self.width and
                    0 <= prev_y < self.height and
                    self.layers[prev_layer][prev_y, prev_x] != -1):

                    cost = wave_grid[prev_layer][prev_y, prev_x]
                    if cost < min_cost:
                        min_cost = cost
                        best_prev = (prev_layer, prev_x, prev_y)

            if best_prev is None:
                raise ValueError("No valid path found")

            path.insert(0, best_prev)
            curr_layer, curr_x, curr_y = best_prev

        return path, final_cost

    def save_routing(self, output_file: str):
        """Save routed nets and their costs to output file"""
        with open(output_file, 'w') as f:
            for net_name, (path, cost) in self.routed_nets.items():
                path_str = ' '.join([f"({layer},{x},{y})" for layer,x,y in path])
                f.write(f"{net_name} Cost: {cost:.2f} Path: {path_str}\n")

def main():
    router = LeeRouter(14, 14, 1, 0)

    router.add_obstacle(0, 8, 1)
    router.add_obstacle(0, 8, 2)
    router.add_obstacle(0, 8, 3)
    router.add_obstacle(0, 8, 4)
    router.add_obstacle(0, 8, 5)
    router.add_obstacle(0, 8, 6)

    router.add_obstacle(0, 9, 1)
    router.add_obstacle(0, 9, 2)
    router.add_obstacle(0, 9, 3)
    router.add_obstacle(0, 9, 4)
    router.add_obstacle(0, 9, 5)
    router.add_obstacle(0, 9, 6)

    router.add_obstacle(0, 7, 6)
    router.add_obstacle(0, 6, 6)
    router.add_obstacle(0, 5, 6)

    router.add_obstacle(0, 7, 7)
    router.add_obstacle(0, 7, 8)
    router.add_obstacle(0, 7, 9)
    router.add_obstacle(0, 7, 10)
    router.add_obstacle(0, 7, 11)

    router.add_obstacle(1, 8, 1)
    router.add_obstacle(1, 8, 2)
    router.add_obstacle(1, 8, 3)
    router.add_obstacle(1, 8, 4)
    router.add_obstacle(1, 8, 5)
    router.add_obstacle(1, 8, 6)

    router.add_obstacle(1, 9, 1)
    router.add_obstacle(1, 9, 2)
    router.add_obstacle(1, 9, 3)
    router.add_obstacle(1, 9, 4)
    router.add_obstacle(1, 9, 5)
    router.add_obstacle(1, 9, 6)

    router.add_obstacle(1, 7, 6)
    router.add_obstacle(1, 6, 6)
    router.add_obstacle(1, 5, 6)

    router.add_obstacle(1, 7, 7)
    router.add_obstacle(1, 7, 8)
    router.add_obstacle(1, 7, 9)
    router.add_obstacle(1, 7, 10)
    router.add_obstacle(1, 7, 11)

    path, cost = router.route_net("net1", [(0, 5, 5), (0, 11, 3)])
    print(f"Net1 routing cost: {cost:.2f}")

    router.save_routing("routing_output.txt")

if __name__ == "__main__":
    main()