from pathlib import Path

from .tile import Tile, TileType


class Level:
    def __init__(self, path: Path) -> None:
        *rows, start = path.read_text(encoding="utf-8").splitlines()
        self.tiles = [[Tile(TileType(symbol)) for symbol in row] for row in rows]
        self.start = tuple(map(int, start.split()))

    def tile_at(self, x: int, y: int) -> Tile | None:
        if 0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[y]):
            return self.tiles[y][x]
        return None
