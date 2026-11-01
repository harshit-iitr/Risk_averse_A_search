import time, heapq
import numpy as np
import torch
from typing import List, Tuple, Dict, Optional, Any
from src.sokoban_env import SokobanEnv
from src.classical_heuristics import manhattan_distance_heuristic
from src.confidence_aware_search import author_state_to_tensor

class SingleModelSearchNode:
    __slots__ = ('state', 'key', 'g', 'h', 'f', 'parent_key', 'action')

    def __init__(self, state: np.ndarray, g: float, h: float, f: float, parent_key=None, action: int=0):
        self.state = state
        self.key = SokobanEnv.state_to_key(state)
        self.g = g
        self.h = h
        self.f = f
        self.parent_key = parent_key
        self.action = action

def run_single_scratch_astar(init_state: np.ndarray, box_targets: List[Tuple[int, int]], model: torch.nn.Module, goal_tensor: torch.Tensor, device: torch.device, max_time: float=360.0, max_expansions: int=1000000, dim: int=10) -> Tuple[bool, int, float, List[int], float]:
    """
    Standard A* using single neural network heuristic without ensembling or gating.
    Matches Paper Learned A* evaluation protocol: f = g + h_nn.
    """
    start_time = time.time()
    init_np = author_state_to_tensor(init_state, box_targets, dim)
    init_tensor = torch.from_numpy(init_np).unsqueeze(0).to(device)
    with torch.no_grad():
        out = model(init_tensor, goal_tensor)
        init_h = out.item() if out.numel() == 1 else out[0].item()
    start_node = SingleModelSearchNode(init_state, g=0.0, h=init_h, f=init_h)
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
            cand_tensors = np.stack([author_state_to_tensor(c[0], box_targets, dim) for c in candidates])
            cand_t = torch.from_numpy(cand_tensors).to(device)
            B = cand_t.shape[0]
            g_batch = goal_tensor.repeat(B, 1, 1, 1)
            with torch.no_grad():
                out_vals = model(cand_t, g_batch)
                h_vals = out_vals.tolist()
                if isinstance(h_vals, float):
                    h_vals = [h_vals]
            for (n_state, n_key, act, new_g), h_val in zip(candidates, h_vals):
                open_dict[n_key] = new_g
                new_f = new_g + h_val
                child = SingleModelSearchNode(n_state, g=new_g, h=h_val, f=new_f, parent_key=current.key, action=act)
                counter += 1
                heapq.heappush(open_heap, (child.f, child.h, counter, child))
    return (False, expansions, float('inf'), [], time.time() - start_time)
