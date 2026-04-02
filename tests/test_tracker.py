"""Tests for Op Kill Tracker."""

import json
import os
import pytest
from src.tracker import load_config


@pytest.fixture
def valid_config(tmp_path):
    config = {
        "players": ["P1", "P2", "P3", "P4", "P5"],
        "op_defaults": {
            "HP": ["Op1", "Op2", "Op3", "Op4", "Op5"],
            "Control": ["Op1", "Op2", "Op3", "Op4", "Op5"],
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    return str(path)


def test_load_valid_config(valid_config):
    config = load_config(valid_config)
    assert config["players"] == ["P1", "P2", "P3", "P4", "P5"]
    assert len(config["op_defaults"]["HP"]) == 5
    assert len(config["op_defaults"]["Control"]) == 5


def test_config_file_missing(tmp_path):
    with pytest.raises(SystemExit):
        load_config(str(tmp_path / "nope.json"))


def test_config_invalid_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{bad json")
    with pytest.raises(SystemExit):
        load_config(str(path))


def test_config_wrong_player_count(tmp_path):
    config = {
        "players": ["P1", "P2"],
        "op_defaults": {
            "HP": ["Op1", "Op2", "Op3", "Op4", "Op5"],
            "Control": ["Op1", "Op2", "Op3", "Op4", "Op5"],
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(SystemExit):
        load_config(str(path))


def test_config_empty_player_name(tmp_path):
    config = {
        "players": ["P1", "", "P3", "P4", "P5"],
        "op_defaults": {
            "HP": ["Op1", "Op2", "Op3", "Op4", "Op5"],
            "Control": ["Op1", "Op2", "Op3", "Op4", "Op5"],
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(SystemExit):
        load_config(str(path))


def test_config_missing_mode(tmp_path):
    config = {
        "players": ["P1", "P2", "P3", "P4", "P5"],
        "op_defaults": {
            "HP": ["Op1", "Op2", "Op3", "Op4", "Op5"],
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(SystemExit):
        load_config(str(path))


def test_config_wrong_op_count(tmp_path):
    config = {
        "players": ["P1", "P2", "P3", "P4", "P5"],
        "op_defaults": {
            "HP": ["Op1", "Op2"],
            "Control": ["Op1", "Op2", "Op3", "Op4", "Op5"],
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(SystemExit):
        load_config(str(path))


def test_config_empty_op_name(tmp_path):
    config = {
        "players": ["P1", "P2", "P3", "P4", "P5"],
        "op_defaults": {
            "HP": ["Op1", "", "Op3", "Op4", "Op5"],
            "Control": ["Op1", "Op2", "Op3", "Op4", "Op5"],
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(SystemExit):
        load_config(str(path))


from src.tracker import TrackerState


def test_initial_state():
    state = TrackerState(5)
    assert state.kills == [0, 0, 0, 0, 0]
    assert state.undo_stack == []
    assert state.last_action == ""


def test_increment():
    state = TrackerState(5)
    state.increment(0)
    assert state.kills == [1, 0, 0, 0, 0]
    assert state.undo_stack == [0]
    assert state.last_action == "+1 Player 1 (total: 1)"


def test_increment_multiple():
    state = TrackerState(5)
    state.increment(0)
    state.increment(0)
    state.increment(2)
    assert state.kills == [2, 0, 1, 0, 0]
    assert state.undo_stack == [0, 0, 2]


def test_undo():
    state = TrackerState(5)
    state.increment(0)
    state.increment(2)
    state.undo()
    assert state.kills == [1, 0, 0, 0, 0]
    assert state.undo_stack == [0]
    assert "Undo" in state.last_action


def test_undo_empty_stack():
    state = TrackerState(5)
    state.undo()
    assert state.kills == [0, 0, 0, 0, 0]
    assert state.last_action == "Nothing to undo"


def test_undo_no_negative():
    state = TrackerState(5)
    state.kills[0] = 0
    state.undo_stack.append(0)  # corrupted state edge case
    state.undo()
    assert state.kills[0] == 0


def test_increment_with_player_names():
    state = TrackerState(5, player_names=["Alpha", "Bravo", "Charlie", "Delta", "Echo"])
    state.increment(1)
    assert state.last_action == "+1 Bravo (total: 1)"
    state.undo()
    assert "Undo" in state.last_action and "Bravo" in state.last_action


import csv
from src.tracker import write_csv


def test_write_csv_creates_file(tmp_path):
    csv_path = str(tmp_path / "op_kills.csv")
    session = {
        "date": "2026-04-02",
        "opponent": "OpTic",
        "map": "Highrise",
        "mode": "HP",
        "players": ["P1", "P2", "P3", "P4", "P5"],
        "operators": ["Op1", "Op2", "Op3", "Op4", "Op5"],
        "kills": [3, 0, 1, 0, 7],
    }
    write_csv(csv_path, session)

    with open(csv_path) as f:
        reader = list(csv.reader(f))
    assert reader[0] == ["date", "opponent", "map", "mode", "player", "operator", "op_kills"]
    assert len(reader) == 6  # header + 5 rows
    assert reader[1] == ["2026-04-02", "OpTic", "Highrise", "HP", "P1", "Op1", "3"]
    assert reader[3] == ["2026-04-02", "OpTic", "Highrise", "HP", "P3", "Op3", "1"]


def test_write_csv_appends(tmp_path):
    csv_path = str(tmp_path / "op_kills.csv")
    session = {
        "date": "2026-04-02",
        "opponent": "OpTic",
        "map": "Highrise",
        "mode": "HP",
        "players": ["P1", "P2", "P3", "P4", "P5"],
        "operators": ["Op1", "Op2", "Op3", "Op4", "Op5"],
        "kills": [1, 1, 1, 1, 1],
    }
    write_csv(csv_path, session)
    write_csv(csv_path, session)

    with open(csv_path) as f:
        reader = list(csv.reader(f))
    assert len(reader) == 11  # 1 header + 5 + 5
    assert reader[0] == ["date", "opponent", "map", "mode", "player", "operator", "op_kills"]
    # No duplicate header
    assert reader[6] != ["date", "opponent", "map", "mode", "player", "operator", "op_kills"]
