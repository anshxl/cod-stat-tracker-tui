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
    with pytest.raises(SystemExit, match="not found"):
        load_config(str(tmp_path / "nope.json"))


def test_config_invalid_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{bad json")
    with pytest.raises(SystemExit, match="Invalid JSON"):
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
    with pytest.raises(SystemExit, match="exactly 5"):
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
    with pytest.raises(SystemExit, match="empty"):
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
    with pytest.raises(SystemExit, match="Control"):
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
    with pytest.raises(SystemExit, match="exactly 5"):
        load_config(str(path))
