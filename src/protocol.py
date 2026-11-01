import hashlib, json
from pathlib import Path
import numpy as np

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

def validate_board(board, boxes=7):
    if board.shape != (10, 10) or not np.isin(board, range(5)).all():
        raise ValueError('Expected a 10x10 board containing tile codes 0..4')
    if any((np.count_nonzero(board == tile) != n for tile, n in [(4, boxes), (2, boxes), (3, 1)])):
        raise ValueError(f'Expected {boxes} boxes, {boxes} free targets, and one player')
    if any((np.any(edge != 0) for edge in (board[0], board[-1], board[:, 0], board[:, -1]))):
        raise ValueError('Expected a closed wall boundary')

def read_boards(path, expected_count=100):
    boards, seen = ([], set())
    for line_no, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip():
            continue
        values = tuple(map(int, line.split()))
        if len(values) != 100 or values in seen:
            raise ValueError(f'Invalid size or duplicate board at line {line_no}')
        board = np.array(values, dtype=np.int32).reshape(10, 10)
        validate_board(board)
        boards.append(board)
        seen.add(values)
    if len(boards) != expected_count:
        raise ValueError(f'Expected {expected_count} boards, found {len(boards)}')
    return boards

def replay_plan(initial, actions, targets=None):
    """Replay without calling the search engine or its transition functions."""
    board = np.array(initial, copy=True)
    if targets is None:
        targets = list(zip(*np.where(board == 2)))
    targets = set(map(tuple, targets))
    directions = {1: (-1, 0, True), 2: (1, 0, True), 3: (0, -1, True), 4: (0, 1, True), 5: (-1, 0, False), 6: (1, 0, False), 7: (0, -1, False), 8: (0, 1, False)}
    players = np.argwhere(board == 3)
    if len(players) != 1 or not targets:
        return False
    r, c = map(int, players[0])
    for action in actions:
        if action not in directions:
            return False
        dr, dc, push = directions[action]
        nr, nc = (r + dr, c + dc)
        if not (0 <= nr < 10 and 0 <= nc < 10):
            return False
        if push:
            br, bc = (nr + dr, nc + dc)
            if not (0 <= br < 10 and 0 <= bc < 10):
                return False
            if board[nr, nc] != 4 or board[br, bc] not in (1, 2):
                return False
            board[br, bc] = 4
        elif board[nr, nc] not in (1, 2):
            return False
        board[r, c] = 2 if (r, c) in targets else 1
        board[nr, nc] = 3
        r, c = (nr, nc)
    return bool(all((board[r, c] == 4 for r, c in targets)))

def smoke_board():
    board = np.zeros((10, 10), dtype=np.int32)
    board[4, 2:5] = [3, 4, 2]
    return board
