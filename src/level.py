from pathlib import Path
import tomllib

from .tile import Tile, TileType


class Level:
    def __init__(self, path: Path) -> None:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        self.tiles = [[Tile(TileType(symbol)) for symbol in row] for row in data["tiles"]]
        self.start = tuple(data["start"])

    def tile_at(self, x: int, y: int) -> Tile | None:
        if 0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[y]):
            return self.tiles[y][x]
        return None
