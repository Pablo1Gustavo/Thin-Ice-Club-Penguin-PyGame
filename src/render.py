from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from .tile import TileType

if TYPE_CHECKING:
    from .game import Game
    from .player import Player


TILE_SIZE = 50
HUD_HEIGHT = 70
HEART_SIZE = 48
BOARD_WIDTH = 19
BOARD_HEIGHT = 15
BOARD_OFFSET_Y = HUD_HEIGHT
BOTTOM_HUD_Y = BOARD_OFFSET_Y + BOARD_HEIGHT * TILE_SIZE
WINDOW_SIZE = (BOARD_WIDTH * TILE_SIZE, BOARD_HEIGHT * TILE_SIZE + HUD_HEIGHT * 2)

PLAYER_FRAME_DURATION_MS = 180
TILE_FRAME_DURATION_MS = 240
MOVEMENT_DURATION_MS = 150
ICE_MELT_DURATION_MS = 500
FALL_DURATION_MS = 1000
LEVEL_TRANSITION_DURATION_MS = 900

ICE_COLOR = (230, 253, 255)
SCORE_COLOR = (30, 60, 150)
HUD_COLOR = (215, 244, 255)
HUD_BORDER_COLOR = (77, 166, 224)


class Render:
    @staticmethod
    def smoothstep(progress: float) -> float:
        return progress * progress * (3 - 2 * progress)

    @staticmethod
    def grid_to_screen(x: int, y: int) -> tuple[int, int]:
        return (x * TILE_SIZE, y * TILE_SIZE + BOARD_OFFSET_Y)

    def __init__(self, screen: pygame.Surface, root: Path) -> None:
        self.screen = screen
        self.animation_elapsed_ms = 0
        self.font = pygame.font.Font(root / "Fonts/Pixeled.ttf", 24)
        self.end_font = pygame.font.Font(None, 48)
        self.fade_overlay = pygame.Surface(WINDOW_SIZE).convert()
        self.fade_overlay.fill((0, 0, 0))
        self.win_message = self.end_font.render("You won! R: restart   Esc: quit", True, SCORE_COLOR)
        self.win_box = self.win_message.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
        self.win_bg_box = self.win_box.inflate(20, 16)

        textures = root / "Textures"
        self.player_images = [
            pygame.transform.smoothscale(
                pygame.image.load(textures / "Player" / f"Player_{index:02d}.png").convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            )
            for index in range(1, 4)
        ]
        self.heart_image = pygame.transform.smoothscale(
            pygame.image.load(textures / "Heart.png").convert_alpha(),
            (HEART_SIZE, HEART_SIZE),
        )
        self.heart_rect = self.heart_image.get_rect(
            topleft=(24, BOTTOM_HUD_Y + (HUD_HEIGHT - HEART_SIZE) // 2)
        )

        def load_tile_frames(name: str, count: int = 1) -> list[pygame.Surface]:
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
            TileType.EMPTY: load_tile_frames("EmptySquare"),
            TileType.WATER: load_tile_frames("Water", 3),
            TileType.ICE: load_tile_frames("Ice"),
            TileType.FINISH: load_tile_frames("FinishSquare", 3),
            TileType.WALL: load_tile_frames("Wall"),
            TileType.DOUBLE_ICE: load_tile_frames("DoubleIce"),
        }
        self.hud_text_values = None

    def reset_level(self, player: Player) -> None:
        self.move_start = self.grid_to_screen(player.x, player.y)
        self.move_elapsed_ms = MOVEMENT_DURATION_MS
        self.melting_tiles = {}

    def player_position(self, player: Player) -> tuple[int, int]:
        progress = min(self.move_elapsed_ms / MOVEMENT_DURATION_MS, 1)
        eased = self.smoothstep(progress)
        target_x, target_y = self.grid_to_screen(player.x, player.y)
        start_x, start_y = self.move_start
        return (
            round(start_x + (target_x - start_x) * eased),
            round(start_y + (target_y - start_y) * eased),
        )

    def start_move(self, player: Player, melted: bool) -> None:
        if melted:
            self.melting_tiles[player.x, player.y] = self.animation_elapsed_ms
        self.move_start = self.player_position(player)
        self.move_elapsed_ms = 0

    def advance(self, elapsed_ms: int) -> None:
        self.animation_elapsed_ms += elapsed_ms
        self.move_elapsed_ms = min(self.move_elapsed_ms + elapsed_ms, MOVEMENT_DURATION_MS)

    def _update_hud_texts(self, game: Game) -> None:
        level_display = min(game.level_index + 1, len(game.level_paths))
        hud_text_values = (
            game.score,
            game.player.lives,
            level_display,
            game.level_score,
            game.level.total_points,
        )
        if hud_text_values != self.hud_text_values:
            render_text = lambda text: self.font.render(text, True, SCORE_COLOR)
            self.score_text = render_text(f"SCORE: {game.score}")
            self.score_rect = self.score_text.get_rect(
                midright=(WINDOW_SIZE[0] - 32, BOTTOM_HUD_Y + HUD_HEIGHT // 2)
            )
            self.lives_text = render_text(f"x{game.player.lives}")
            self.lives_rect = self.lives_text.get_rect(
                midleft=(self.heart_rect.right + 16, BOTTOM_HUD_Y + HUD_HEIGHT // 2)
            )
            self.level_text = render_text(f"LEVEL {level_display}")
            self.level_rect = self.level_text.get_rect(
                midleft=(32, HUD_HEIGHT // 2)
            )
            self.progress_text = render_text(
                f"{game.level_score} / {game.level.total_points}"
            )
            self.progress_rect = self.progress_text.get_rect(
                midright=(WINDOW_SIZE[0] - 32, HUD_HEIGHT // 2)
            )
            self.hud_text_values = hud_text_values

    def _draw_tiles(self, game: Game) -> None:
        tile_frame_index = self.animation_elapsed_ms // TILE_FRAME_DURATION_MS
        tile_frames = {
            kind: frames[tile_frame_index % len(frames)]
            for kind, frames in self.tile_images.items()
        }
        for y, row in enumerate(game.level.tiles):
            for x, tile in enumerate(row):
                position = self.grid_to_screen(x, y)
                self.screen.blit(tile_frames[tile.kind], position)
                if tile.kind is TileType.WATER and (x, y) in self.melting_tiles:
                    elapsed = self.animation_elapsed_ms - self.melting_tiles[x, y]
                    if elapsed >= ICE_MELT_DURATION_MS:
                        del self.melting_tiles[x, y]
                    else:
                        alpha = round(255 * (1 - self.smoothstep(elapsed / ICE_MELT_DURATION_MS)))
                        ice_overlay = tile_frames[TileType.ICE].copy()
                        ice_overlay.set_alpha(alpha)
                        self.screen.blit(ice_overlay, position)

    def _draw_hud_bar(self, y: int, border_y: int) -> None:
        pygame.draw.rect(self.screen, HUD_COLOR, (0, y, WINDOW_SIZE[0], HUD_HEIGHT))
        pygame.draw.rect(self.screen, HUD_BORDER_COLOR, (0, border_y, WINDOW_SIZE[0], 4))

    def _draw_top_hud(self) -> None:
        self._draw_hud_bar(0, HUD_HEIGHT - 4)
        self.screen.blit(self.level_text, self.level_rect)
        self.screen.blit(self.progress_text, self.progress_rect)

    def _draw_bottom_hud(self) -> None:
        self._draw_hud_bar(BOTTOM_HUD_Y, BOTTOM_HUD_Y)
        self.screen.blit(self.heart_image, self.heart_rect)
        self.screen.blit(self.lives_text, self.lives_rect)
        self.screen.blit(self.score_text, self.score_rect)

    def _draw_player(self, game: Game) -> None:
        frame_index = (self.animation_elapsed_ms // PLAYER_FRAME_DURATION_MS) % len(self.player_images)
        player_image = self.player_images[frame_index]
        player_position = self.player_position(game.player)
        if game.fall_elapsed_ms is not None:
            shrink_progress = max(
                0,
                (game.fall_elapsed_ms - MOVEMENT_DURATION_MS) / (FALL_DURATION_MS - MOVEMENT_DURATION_MS),
            )
            size = max(1, round(TILE_SIZE * (1 - shrink_progress**2)))
            player_image = pygame.transform.smoothscale(player_image, (size, size))
            player_position = player_image.get_rect(
                center=(player_position[0] + TILE_SIZE // 2, player_position[1] + TILE_SIZE // 2)
            )
        self.screen.blit(player_image, player_position)

    def _draw_win_message(self) -> None:
        pygame.draw.rect(self.screen, ICE_COLOR, self.win_bg_box)
        self.screen.blit(self.win_message, self.win_box)

    def _draw_transition(self, game: Game) -> None:
        if game.transition_elapsed_ms is None:
            return
        midpoint = LEVEL_TRANSITION_DURATION_MS // 2
        progress = (
            min(game.transition_elapsed_ms, LEVEL_TRANSITION_DURATION_MS - game.transition_elapsed_ms)
            / midpoint
        )
        self.fade_overlay.set_alpha(round(255 * self.smoothstep(progress)))
        self.screen.blit(self.fade_overlay, (0, 0))

    def draw(self, game: Game) -> None:
        self._update_hud_texts(game)
        self._draw_tiles(game)
        self._draw_top_hud()
        self._draw_bottom_hud()
        self._draw_player(game)
        if game.won:
            self._draw_win_message()
        self._draw_transition(game)
        pygame.display.flip()
