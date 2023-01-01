from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Tuple

from pyparsing import Any

from pharcobial.constants import MAP_VOID
from pharcobial.logging import game_logger
from pharcobial.managers.base import BaseManager
from pharcobial.types import MapID, Position, Positional, SpriteID, TileKey
from pharcobial.utils.loaders import safe_load, safe_load_csv
from pharcobial.utils.paths import game_paths


@dataclass
class MapCharacterData:
    sprite_id: SpriteID
    location: Position

    @classmethod
    def parse_obj(cls, obj: Dict) -> "MapCharacterData":
        location = Position.parse_coordinates(**obj["location"])
        return cls(sprite_id=obj["sprite_id"], location=location)


@dataclass
class MapMetaData:
    map_id: MapID
    tile_set: Dict[TileKey, Dict[str, Any]]
    player: MapCharacterData
    npcs: List[MapCharacterData]

    @classmethod
    def parse_file(cls, path: Path) -> "MapMetaData":
        data = safe_load(path)
        data["player"] = MapCharacterData.parse_obj(data["player"])

        npc_list = list(data.get("npcs", []))
        data["npcs"] = []
        for npc_obj in npc_list:
            is_multiple = npc_obj.get("multiple", False)
            if is_multiple:
                sprite_id_format = npc_obj.get("sprite_id")
                locations = npc_obj["locations"]
                for idx, location in enumerate(locations):
                    sprite_id = sprite_id_format.format(x=idx)
                    location = Position.parse_coordinates(**location)
                    data["npcs"].append(MapCharacterData(sprite_id=sprite_id, location=location))

            else:
                data["npcs"].append(MapCharacterData.parse_obj(npc_obj))

        if MAP_VOID not in data["tile_set"]:
            data["tile_set"][MAP_VOID] = {"gfx": None, "collision": True}

        return cls(**data)


@dataclass
class Map:
    map_id: MapID
    metadata: MapMetaData
    tiles: List[List[TileKey]]

    @classmethod
    def parse_file(cls, path: Path) -> "Map":
        metadata_file = path.parent / f"{path.stem}.json"
        metadata = MapMetaData.parse_file(metadata_file)
        tiles = safe_load_csv(path)
        return cls(map_id=path.stem, tiles=tiles, metadata=metadata)

    @property
    def width(self) -> int:
        return len(self.tiles[0])

    @property
    def height(self) -> int:
        return len(self.tiles)

    def __iter__(self) -> Iterator[List[TileKey]]:
        yield from self.tiles

    def __getitem__(self, key: int | slice) -> List[TileKey] | List[List[TileKey]]:
        return self.tiles[key]


class MapManager(BaseManager):
    def __init__(self) -> None:
        super().__init__()
        self.active = self.load(self.options.map_id)

    def __repr__(self) -> str:
        return repr(self.active)

    @property
    def map_id(self) -> MapID | None:
        return self.active.map_id

    @property
    def player_start(self) -> Positional:
        return self.active.metadata.player.location

    @property
    def npcs_start(self) -> Iterator[Tuple[SpriteID, Positional]]:
        for npc in self.active.metadata.npcs:
            yield npc.sprite_id, npc.location

    @property
    def tile_set(self) -> Dict[TileKey, Dict[str, Any]]:
        return self.active.metadata.tile_set

    @property
    def width(self) -> int:
        return self.active.width

    @property
    def height(self) -> int:
        return self.active.height

    def __iter__(self):
        yield from self.active

    def __getitem__(self, idx: int | slice):
        return self.active[idx]

    def load(self, map_id: MapID) -> Map:
        file_path = game_paths.get_map(map_id)
        loaded_map = Map.parse_file(file_path)
        self.active = loaded_map
        return loaded_map

    def validate(self):
        assert self.player_start
        assert self.active
        game_logger.debug("Map ready.")

    def reset(self):
        self.load(self.active.map_id)


map_manager = MapManager()
