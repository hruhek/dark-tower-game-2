from dark_fort.game.dungeon import DungeonBuilder
from dark_fort.game.models import Room


class TestDungeonBuilder:
    def test_build_room_returns_room(self):
        builder = DungeonBuilder()
        room = builder.build_room()
        assert isinstance(room, Room)
        assert room.shape
        assert room.doors >= 1

    def test_build_room_increments_counter(self):
        builder = DungeonBuilder()
        room0 = builder.build_room()
        room1 = builder.build_room()
        assert room0.id == 0
        assert room1.id == 1

    def test_build_entrance_is_explored(self):
        builder = DungeonBuilder()
        room = builder.build_room(is_entrance=True)
        assert room.explored is True

    def test_build_non_entrance_is_unexplored(self):
        builder = DungeonBuilder()
        room = builder.build_room(is_entrance=False)
        assert room.explored is False

    def test_connect_adds_bidirectional_connections(self):
        builder = DungeonBuilder()
        room_a = builder.build_room()
        room_b = builder.build_room()
        builder.connect(room_a, room_b)
        assert room_b.id in room_a.connections
        assert room_a.id in room_b.connections

    def test_build_dungeon_minimum_rooms(self):
        builder = DungeonBuilder()
        rooms = builder.build_dungeon(min_rooms=5)
        assert len(rooms) >= 5

    def test_build_dungeon_first_room_is_entrance(self):
        builder = DungeonBuilder()
        rooms = builder.build_dungeon(min_rooms=3)
        assert rooms[0].explored is True

    def test_build_dungeon_rooms_are_connected(self):
        builder = DungeonBuilder()
        rooms = builder.build_dungeon(min_rooms=5)
        connected_ids: set[int] = set()
        for room in rooms:
            connected_ids.update(room.connections)
        assert len(connected_ids) >= len(rooms) - 1
