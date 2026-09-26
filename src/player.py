from dataclasses import dataclass


@dataclass
class Player:
    x: int
    y: int
    lives: int = 3

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def reset_position(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def lose_life(self) -> None:
        if self.lives > 0:
            self.lives -= 1

    def is_alive(self) -> bool:
        return self.lives > 0
