from pathlib import Path

import pygame

from .level import Level
from .player import Player
from .tile import TileType


ROOT = Path(__file__).resolve().parent.parent

TILE_SIZE = 50
HUD_HEIGHT = 70
HEART_SIZE = 48

PLAYER_FRAME_COUNT = 3

PLAYER_FRAME_DURATION_MS = 180
TILE_FRAME_DURATION_MS = 240

BOARD_WIDTH = 19
BOARD_HEIGHT = 15

WINDOW_SIZE = (BOARD_WIDTH * TILE_SIZE, BOARD_HEIGHT * TILE_SIZE + HUD_HEIGHT)

ICE_COLOR = (230, 253, 255)
SCORE_COLOR = (30, 60, 150)
HUD_COLOR = (215, 244, 255)
HUD_BORDER_COLOR = (77, 166, 224)

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
        self.font = pygame.font.Font(ROOT / "Fonts/Pixeled.ttf", 24)
        self.end_font = pygame.font.Font(None, 48)

        textures = ROOT / "Textures"
        player_textures = textures / "Player"
        self.player_images = [
            pygame.transform.smoothscale(
                pygame.image.load(player_textures / f"Player_{index:02d}.png").convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            )
            for index in range(1, PLAYER_FRAME_COUNT + 1)
        ]
        self.animation_elapsed_ms = 0
        self.heart_image = pygame.transform.smoothscale(
            pygame.image.load(textures / "Heart.png").convert_alpha(),
            (HEART_SIZE, HEART_SIZE),
        )

        def load_tile_frames(name: str, count: int) -> list[pygame.Surface]:
            paths = (
                [textures / name / f"{name}_{index:02d}.png" for index in range(1, count + 1)]
                if count > 1
                else [textures / f"{name}.png"]
            )
            return [
                pygame.transform.scale(
                    pygame.image.load(path).convert_alpha(),
                    (TILE_SIZE, TILE_SIZE),
                )
                for path in paths
            ]

        self.tile_images = {
            TileType.EMPTY: load_tile_frames("EmptySquare", 1),
            TileType.WATER: load_tile_frames("Water", 3),
            TileType.ICE: load_tile_frames("Ice", 1),
            TileType.FINISH: load_tile_frames("FinishSquare", 3),
            TileType.WALL: load_tile_frames("Wall", 1),
            TileType.DOUBLE_ICE: load_tile_frames("DoubleIce", 1),
        }
        self.hud_text_values = None

        pygame.mixer.music.load(ROOT / "Sounds/GameMusic.mp3")
        pygame.mixer.music.set_volume(0.65)
        pygame.mixer.music.play(-1)

        self.level_paths = sorted(
            (ROOT / "Levels").glob("level*.toml"),
            key=lambda path: int(path.stem.removeprefix("level")),
        )
        self.held_actions = set()
        self.restart()

    def restart(self) -> None:
        self.score = 0
        self.level_score = 0
        self.level_index = 0
        self.won = False
        self.player = Player(0, 0)
        self.load_level()

    def load_level(self) -> None:
        self.level = Level(self.level_paths[self.level_index])
        self.player.reset_position(*self.level.start)

    def move_player(self, dx: int, dy: int) -> None:
        x, y = self.player.x + dx, self.player.y + dy
        destination = self.level.tile_at(x, y)
        if destination is None or not destination.walkable:
            return

        points = self.level.tile_at(self.player.x, self.player.y).leave()
        self.score += points
        self.level_score += points
        self.player.move(dx, dy)

        match destination.kind:
            case TileType.WATER:
                self.score -= self.level_score
                self.level_score = 0
                self.player.lose_life()
                if not self.player.is_alive():
                    self.restart()
                else:
                    self.load_level()
            case TileType.FINISH:
                self.level_score = 0
                self.level_index += 1
                if self.level_index == len(self.level_paths):
                    self.won = True
                else:
                    self.load_level()

    def draw(self) -> None:
        tile_frame_index = self.animation_elapsed_ms // TILE_FRAME_DURATION_MS
        tile_frames = {
            kind: frames[tile_frame_index % len(frames)]
            for kind, frames in self.tile_images.items()
        }
        for y, row in enumerate(self.level.tiles):
            for x, tile in enumerate(row):
                self.screen.blit(tile_frames[tile.kind], (x * TILE_SIZE, y * TILE_SIZE))

        hud_y = BOARD_HEIGHT * TILE_SIZE
        pygame.draw.rect(self.screen, HUD_COLOR, (0, hud_y, WINDOW_SIZE[0], HUD_HEIGHT))
        pygame.draw.rect(self.screen, HUD_BORDER_COLOR, (0, hud_y, WINDOW_SIZE[0], 4))
        heart_rect = self.heart_image.get_rect(topleft=(24, hud_y + (HUD_HEIGHT - HEART_SIZE) // 2))
        self.screen.blit(self.heart_image, heart_rect)
        hud_text_values = (self.score, self.player.lives)
        if hud_text_values != self.hud_text_values:
            self.score_text = self.font.render(f"SCORE: {self.score}", True, SCORE_COLOR)
            self.lives_text = self.font.render(f"x{self.player.lives}", True, SCORE_COLOR)
            self.hud_text_values = hud_text_values
        self.screen.blit(self.score_text, self.score_text.get_rect(midright=(WINDOW_SIZE[0] - 32, hud_y + HUD_HEIGHT // 2)))
        self.screen.blit(self.lives_text, self.lives_text.get_rect(midleft=(heart_rect.right + 16, hud_y + HUD_HEIGHT // 2)))
        frame_index = (self.animation_elapsed_ms // PLAYER_FRAME_DURATION_MS) % len(self.player_images)
        self.screen.blit(self.player_images[frame_index], (self.player.x * TILE_SIZE, self.player.y * TILE_SIZE))

        if self.won:
            message = self.end_font.render("You won! R: restart   Esc: quit", True, SCORE_COLOR)
            box = message.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            pygame.draw.rect(self.screen, ICE_COLOR, box.inflate(20, 16))
            self.screen.blit(message, box)

        pygame.display.flip()

    def run(self) -> None:
        running = True
        clock = pygame.time.Clock()
        self.draw()
        while running:
            self.animation_elapsed_ms += clock.tick(30)
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
