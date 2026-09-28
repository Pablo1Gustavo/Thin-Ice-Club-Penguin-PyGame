from pathlib import Path

import pygame

from .level import Level
from .player import Player
from .render import (
    FALL_DURATION_MS,
    LEVEL_TRANSITION_DURATION_MS,
    WINDOW_SIZE,
    Render,
)
from .tile import TileType


ROOT = Path(__file__).resolve().parent.parent

DIRECTIONS = {
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
}


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.key.set_repeat(300, 200)
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption("Thin Ice")
        self.renderer = Render(self.screen, ROOT)

        pygame.mixer.music.load(ROOT / "Sounds/GameMusic.mp3")
        pygame.mixer.music.set_volume(0.65)

        self.level_paths = sorted(
            (ROOT / "Levels").glob("level*.toml"),
            key=lambda path: int(path.stem.removeprefix("level")),
        )
        self.held_actions = set()
        self.restart()

    def restart(self) -> None:
        self.transition_elapsed_ms = None
        self.score = 0
        self.level_index = 0
        self.won = False
        self.player = Player(0, 0)
        self.held_actions.clear()
        if pygame.mixer.get_init():
            pygame.mixer.music.play(-1)
        self.load_level()

    def load_level(self) -> None:
        self.level_score = 0
        self.level = Level(self.level_paths[self.level_index])
        self.player.reset_position(*self.level.start)
        self.renderer.reset_level(self.player)
        self.fall_elapsed_ms = None

    def move_player(self, dx: int, dy: int) -> None:
        if self.fall_elapsed_ms is not None or self.transition_elapsed_ms is not None:
            return

        x, y = self.player.x + dx, self.player.y + dy
        destination = self.level.tile_at(x, y)
        if destination is None or not destination.walkable:
            return

        previous_tile = self.level.tile_at(self.player.x, self.player.y)
        points = previous_tile.leave()
        self.score += points
        self.level_score += points
        self.renderer.start_move(self.player, bool(points))
        self.player.move(dx, dy)

        match destination.kind:
            case TileType.WATER:
                self.score -= self.level_score
                self.level_score = 0
                self.player.lose_life()
                self.fall_elapsed_ms = 0
            case TileType.FINISH:
                self.transition_elapsed_ms = 0

    def advance_animations(self, elapsed_ms: int) -> None:
        self.renderer.advance(elapsed_ms)
        if self.fall_elapsed_ms is not None:
            self.fall_elapsed_ms += elapsed_ms
            if self.fall_elapsed_ms >= FALL_DURATION_MS:
                if self.player.is_alive:
                    self.load_level()
                else:
                    self.restart()
        if self.transition_elapsed_ms is not None:
            previous_elapsed = self.transition_elapsed_ms
            self.transition_elapsed_ms = min(previous_elapsed + elapsed_ms, LEVEL_TRANSITION_DURATION_MS)
            midpoint = LEVEL_TRANSITION_DURATION_MS // 2
            if previous_elapsed < midpoint <= self.transition_elapsed_ms:
                self.level_index += 1
                if self.level_index == len(self.level_paths):
                    self.won = True
                else:
                    self.load_level()
            if self.transition_elapsed_ms >= LEVEL_TRANSITION_DURATION_MS:
                self.transition_elapsed_ms = None

    def draw(self) -> None:
        self.renderer.draw(self)

    def run(self) -> None:
        running = True
        clock = pygame.time.Clock()
        self.draw()
        while running:
            self.advance_animations(clock.tick(60))
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case pygame.KEYUP:
                        self.held_actions.discard(event.key)
                    case pygame.KEYDOWN:
                        if event.key in (pygame.K_F5, pygame.K_F11):
                            if event.key in self.held_actions:
                                continue
                            self.held_actions.add(event.key)
                        match event.key:
                            case pygame.K_ESCAPE:
                                running = False
                            case pygame.K_F11:
                                try:
                                    pygame.display.toggle_fullscreen()
                                except pygame.error as error:
                                    print(f"Fullscreen unavailable: {error}")
                            case pygame.K_F5:
                                self.restart()
                            case pygame.K_r if self.won:
                                self.restart()
                            case key if not self.won and key in DIRECTIONS:
                                self.move_player(*DIRECTIONS[key])
            if running:
                self.draw()

        pygame.quit()
