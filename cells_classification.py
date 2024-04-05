from base.client.map import Map
from base.client.constants import *


def is_enemy_cell(gamemap: Map, x, y):
    if x < 0 or x >= gamemap.cols or y < 0 or y >= gamemap.rows:
        return False
    return gamemap.grid[y][x].tile not in [TILE_OBSTACLE, TILE_FOG, TILE_MOUNTAIN, TILE_EMPTY] and \
        gamemap.grid[y][x].tile != gamemap.player_index


def is_empty_cell(gamemap: Map, x, y):
    if x < 0 or x >= gamemap.cols or y < 0 or y >= gamemap.rows:
        return False
    return gamemap.grid[y][x].tile == TILE_EMPTY and not gamemap.grid[y][x].isCity


def is_my_cell(gamemap: Map, x, y):
    if x < 0 or x >= gamemap.cols or y < 0 or y >= gamemap.rows:
        return False
    return gamemap.grid[y][x].tile == gamemap.player_index


def is_simple_cell(gamemap: Map, x, y):
    if x < 0 or x >= gamemap.cols or y < 0 or y >= gamemap.rows:
        return False
    return gamemap.grid[y][x].tile not in [TILE_OBSTACLE, TILE_MOUNTAIN] and not gamemap.grid[y][
        x].isCity and not gamemap.grid[y][x].isGeneral

