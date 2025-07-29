# special_cases.py
from log import log_info, log_warning
from util import is_valid_color, normalize_color


def needs_split(text):
    # Alle Texte, die einen leeren ""-Eintrag im extra-Feld benötigen
    SPECIAL_CASES = {"Pets"}  # Füge hier alle gewünschten Ausnahmen hinzu
    return text in SPECIAL_CASES


def get_fallback_path(item_name, type_prefix):
    """Fallback-Modellpfad je nach Item"""
    if item_name == "chest":
        return {
            "base": "minecraft:item/chest",
            "model": {
                "texture": "minecraft:normal",
                "type": "minecraft:chest"
            },
            "type": "minecraft:special"
        }
        
    elif item_name == "clock":
        return generate_clock_model()
        
    else:
        return {
            "model": f"{type_prefix}/{item_name}",
            "type": "model"
        }


def generate_clock_model():
    def generate_entries():
        entries = []
        for i in range(64):
            entries.append({
                "model": {
                    "model": f"minecraft:item/clock_{i:02}",
                    "type": "minecraft:model"
                },
                "threshold": i - 0.5 if i > 0 else 0.0
            })
        # Letzter Durchlauf mit clock_00 bei 63.5
        entries.append({
            "model": {
                "model": "minecraft:item/clock_00",
                "type": "minecraft:model"
            },
            "threshold": 63.5
        })
        return entries

    def make_range_dispatch(source):
        return {
            "entries": generate_entries(),
            "property": "minecraft:time",
            "scale": 64.0,
            "source": source,
            "type": "minecraft:range_dispatch"
        }

    return {
        "cases": [
            {
                "model": make_range_dispatch("daytime"),
                "when": "minecraft:overworld"
            }
        ],
        "fallback": make_range_dispatch("random"),
        "property": "minecraft:context_dimension",
        "type": "minecraft:select"
    }


def handle_fishing_rod_cast(item_id, model_path):
    """Modellstruktur für Fishing Rod mit Cast"""
    return {
        "predicate": "fishing_rod/cast",
        "property": "fishing_rod/cast",
        "type": "condition",
        "on_true": {
            "model": f"skyblock:skyblock/{model_path}_cast",
            "type": "model"
        },
        "on_false": {
            "model": f"skyblock:skyblock/{model_path}",
            "type": "model"
        }
    }


def handle_bow_pull(item_id, model_path):
    """Erzeugt das Modell für einen Bogen mit Pull-Animation."""

    return {
        "predicate": "custom_data",
        "property": "component",
        "type": "condition",
        "value": {
            "id": item_id
        },
        "on_true": {
            "property": "using_item",
            "type": "condition",
            "on_true": {
                "property": "use_duration",
                "scale": 0.05,
                "type": "range_dispatch",
                "entries": [
                    {
                        "threshold": 0.65,
                        "model": {
                            "model": f"skyblock:skyblock/{model_path}_pulling_1",
                            "type": "model"
                        }
                    },
                    {
                        "threshold": 0.9,
                        "model": {
                            "model": f"skyblock:skyblock/{model_path}_pulling_2",
                            "type": "model"
                        }
                    }
                ],
                "fallback": {
                    "model": f"skyblock:skyblock/{model_path}_pulling_0",
                    "type": "model"
                }
            },
            "on_false": {
                "model": f"skyblock:skyblock/{model_path}",
                "type": "model"
            }
        },
        "on_false": {
            "model": "item/bow",
            "type": "model"
        }
    }


def handle_player_head(entries):
    # Erzeuge die Fälle aus entries, wie bei name_cases
    name_cases = []

    for item_id, model_path, _ in entries:
        if ":" in item_id:
            try:
                color, text = item_id.split(":", 1)
                color = normalize_color(color)

                if not is_valid_color(color):
                    log_warning(f"Ungültige Farbe '{color}' bei '{item_id}', wird übersprungen.")
                    continue
            except ValueError:
                log_warning(f"Ungültiges Format in ID: {item_id}")

            case = {
                "when": [
                    {
                        "italic": False,
                        "extra": [
                            {
                                "color": color,
                                "text": text
                            }
                        ],
                        "text": ""
                    }
                ],
                "model": {
                    "type": "model",
                    "model": f"skyblock:skyblock/{model_path}"
                }
            }
            name_cases.append(case)
    return {
        "model": {
            "fallback": {
                "type": "special",
                "base": "item/template_skull",
                "model": {
                    "type": "head",
                    "kind": "player"
                }
            },
            "type": "select",
            "property": "component",
            "component": "custom_name",
            "cases": name_cases
        }
    }
