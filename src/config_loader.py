from pathlib import Path

import yaml


def load_config():
    """
    Load application configuration from config/config.yaml.
    """
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "config" / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)