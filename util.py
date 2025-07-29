# util.py
import os
import shutil


def read_cfg(filepath):
    result = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # Kommentare/Leerzeilen überspringen
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Wenn der Key "target" ist und der Pfad %appdata% enthält
                if key.lower() == "target" and "%appdata%" in value.lower():
                    appdata_path = os.environ.get("APPDATA")
                    # Ersetze %appdata% (case-insensitive) durch den tatsächlichen Pfad
                    value = value.replace("%appdata%", appdata_path)
                    value = value.replace("%APPDATA%", appdata_path)  # für Sicherheit

                result[key] = value
    return result


COLOR_ALIASES = {
    "purple": "dark_purple",
    "lightpurple": "light_purple",
    "grey": "gray"
}


def normalize_color(color: str) -> str:
    return COLOR_ALIASES.get(color, color)


def is_valid_color(color: str) -> bool:
    return normalize_color(color) in {
        "black", "dark_blue", "dark_green", "dark_aqua", "dark_red",
        "dark_purple", "gold", "gray", "dark_gray", "blue",
        "green", "aqua", "red", "light_purple", "yellow", "white"
    }


def clear_target_folder(cfg):
    target_root = cfg.get("target")
    if not target_root:
        raise ValueError("Config enthält keinen 'target'-Pfad.")

    if os.path.exists(target_root):
        shutil.rmtree(target_root)