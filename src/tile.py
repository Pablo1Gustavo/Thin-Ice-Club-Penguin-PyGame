from dataclasses import dataclass
from enum import StrEnum


class TileType(StrEnum):
    EMPTY = "0"
    WATER = "1"
    ICE = "2"
    FINISH = "3"
    WALL = "4"
    DOUBLE_ICE = "5"


@dataclass
class Tile:
    kind: TileType

    @property
    def walkable(self) -> bool:
        return self.kind not in (TileType.EMPTY, TileType.WALL)

    def leave(self) -> int:
        """Melt this tile and return the points earned."""
        match self.kind:
            case TileType.DOUBLE_ICE:
                self.kind = TileType.ICE
            case TileType.ICE:
                self.kind = TileType.WATER
                return 1
        return 0
