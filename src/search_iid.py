import time, heapq
import numpy as np
import torch
from typing import List, Tuple, Dict, Optional, Any
from src.sokoban_env import SokobanEnv
from src.classical_heuristics import manhattan_distance_heuristic
from src.confidence_aware_search import author_state_to_tensor

class SearchNode:
    __slots__ = ('state', 'key', 'g', 'h', 'f', 'parent_key', 'action')

    def __init__(self, state: np.ndarray, g: float, h: float, f: float, parent_key=None, action=0):
        self.state = state
        self.key = SokobanEnv.state_to_key(state)
        self.g = g
        self.h = h
        self.f = f
        self.parent_key = parent_key
        self.action = action

def run_batched_paper_search(init_state: np.ndarray, box_targets: List[Tuple[int, int]], model: torch.nn.Module, goal_tensor: torch.Tensor, device: torch.device, alg: str='astar', max_time: float=600.0, max_expansions: int=100000, dim: int=10) -> Tuple[bool, int, float, List[int], float]:
    """
    Batched neural forward evaluation matching Chrestien et al. (NeurIPS 2023).
    A* priority:   f = g + h_nn, secondary: h_nn, tertiary: counter
    GBFS priority: f = h_nn,     secondary: counter
    """
    start_time = time.time()
    init_tensor = torch.from_numpy(author_state_to_tensor(init_state, box_targets, dim)).unsqueeze(0).to(device)
    with torch.no_grad():
        init_h = model(init_tensor, goal_tensor).item()
    init_f = init_h if alg == 'gbfs' else 0.0 + init_h
    start_node = SearchNode(init_state, g=0.0, h=init_h, f=init_f)
    open_heap = []
    heapq.heappush(open_heap, (start_node.f, start_node.h, 0, start_node))
    open_dict = {start_node.key: start_node.g}
    closed_dict = {}
    counter = 0
    expansions = 0
    while open_heap:
        if time.time() - start_time > max_time or expansions >= max_expansions:
            return (False, expansions, float('inf'), [], time.time() - start_time)
        _, _, _, current = heapq.heappop(open_heap)
        if current.key in closed_dict:
            continue
        closed_dict[current.key] = current
        expansions += 1
        if SokobanEnv.is_goal(current.state, box_targets):
            elapsed = time.time() - start_time
            actions = []
            curr = current
            while curr.parent_key is not None:
                actions.append(curr.action)
                curr = closed_dict[curr.parent_key]
            actions.reverse()
            return (True, expansions, current.g, actions, elapsed)
        next_states, act_nos, costs = SokobanEnv.get_neighbors(current.state, box_targets, dim)
        candidates = []
        for n_state, act, cost in zip(next_states, act_nos, costs):
            n_key = SokobanEnv.state_to_key(n_state)
            new_g = current.g + cost
            if n_key in closed_dict and closed_dict[n_key].g <= new_g:
                continue
            if n_key in open_dict and open_dict[n_key] <= new_g:
                continue
            candidates.append((n_state, n_key, act, new_g))
        if candidates:
            non_goal_indices = []
            h_vals = [0.0] * len(candidates)
            for idx, c in enumerate(candidates):
                if SokobanEnv.is_goal(c[0], box_targets):
                    h_vals[idx] = 0.0
                else:
                    non_goal_indices.append(idx)
            if non_goal_indices:
                tensors = [author_state_to_tensor(candidates[i][0], box_targets, dim) for i in non_goal_indices]
                batch_t = torch.from_numpy(np.stack(tensors)).to(device)
                goals_t = goal_tensor.repeat(len(non_goal_indices), 1, 1, 1)
                with torch.no_grad():
                    preds = model(batch_t, goals_t).flatten().cpu().tolist()
                for i, pred in zip(non_goal_indices, preds):
                    h_vals[i] = pred
            for (n_state, n_key, act, new_g), h_val in zip(candidates, h_vals):
                open_dict[n_key] = new_g
                new_f = h_val if alg == 'gbfs' else new_g + h_val
                child = SearchNode(n_state, g=new_g, h=h_val, f=new_f, parent_key=current.key, action=act)
                counter += 1
                heapq.heappush(open_heap, (child.f, child.h, counter, child))
    return (False, expansions, float('inf'), [], time.time() - start_time)

def run_classical_astar(init_state: np.ndarray, box_targets: List[Tuple[int, int]], max_time: float=600.0, max_expansions: int=150000, dim: int=10) -> Tuple[bool, int, float, List[int], float]:
    """
    Classical Admissible A* using Hungarian Manhattan distance.
    """
    start_time = time.time()
    init_h = manhattan_distance_heuristic(init_state, box_targets)
    start_node = SearchNode(init_state, g=0.0, h=init_h, f=init_h)
    open_heap = []
    heapq.heappush(open_heap, (start_node.f, start_node.h, 0, start_node))
    open_dict = {start_node.key: start_node.g}
    closed_dict = {}
    counter = 0
    expansions = 0
    while open_heap:
        if time.time() - start_time > max_time or expansions >= max_expansions:
            return (False, expansions, float('inf'), [], time.time() - start_time)
        _, _, _, current = heapq.heappop(open_heap)
        if current.key in closed_dict:
            continue
        closed_dict[current.key] = current
        expansions += 1
        if SokobanEnv.is_goal(current.state, box_targets):
            elapsed = time.time() - start_time
            actions = []
            curr = current
            while curr.parent_key is not None:
                actions.append(curr.action)
                curr = closed_dict[curr.parent_key]
            actions.reverse()
            return (True, expansions, current.g, actions, elapsed)
        next_states, act_nos, costs = SokobanEnv.get_neighbors(current.state, box_targets, dim)
        for n_state, act, cost in zip(next_states, act_nos, costs):
            n_key = SokobanEnv.state_to_key(n_state)
            new_g = current.g + cost
            if n_key in closed_dict and closed_dict[n_key].g <= new_g:
                continue
            if n_key in open_dict and open_dict[n_key] <= new_g:
                continue
            open_dict[n_key] = new_g
            h_val = manhattan_distance_heuristic(n_state, box_targets)
            child = SearchNode(n_state, g=new_g, h=h_val, f=new_g + h_val, parent_key=current.key, action=act)
            counter += 1
            heapq.heappush(open_heap, (child.f, child.h, counter, child))
    return (False, expansions, float('inf'), [], time.time() - start_time)
