# writer.py

import os
import json
import shutil

from special_cases import (
    get_fallback_path,
    handle_fishing_rod_cast,
    handle_bow_pull,
    handle_player_head,
    needs_split
)
from util import is_valid_color, normalize_color
from log import log_info, log_warning


# === Pfad-Helferfunktionen ===
def get_model_path(target_root, model_path):
    return os.path.join(target_root, "assets", "skyblock", "models", "skyblock", f"{model_path}.json")


def get_texture_path(target_root, model_path):
    return os.path.join(target_root, "assets", "skyblock", "textures", "skyblock", f"{model_path}.png")


def get_main_model_path(target_root, item_name):
    return os.path.join(target_root, "assets", "minecraft", "items", f"{item_name}.json")


# === Strukturaufbau für Modell ===
def build_model_structure(entries, fallback_item, type_prefix):
    if fallback_item == "player_head":
        return handle_player_head(entries)

    fallback = get_fallback_path(fallback_item, type_prefix)
    result = {}
    name_cases = []
    data_entries = []

    for item_id, model_path, _ in entries:
        if ":" in item_id:
            try:
                color, text = item_id.split(":", 1)
                color = normalize_color(color)

                if not is_valid_color(color):
                    log_warning(f"Ungültige Farbe '{color}' bei '{item_id}', wird übersprungen.")
                    continue
            except ValueError:
                raise ValueError(f"Ungültiges Format in ID: {item_id}")

            case = {
                "model": {
                    "model": f"skyblock:skyblock/{model_path}",
                    "type": "model"
                },
                "when": [{
                    "extra": (
                        [{"color": color, "text": ""}] if needs_split(text) else []
                    ) + [{"color": color, "text": text}],
                    "italic": False,
                    "text": ""
                }]
            }
            name_cases.append(case)
        else:
            data_entries.append((item_id, model_path))

    if data_entries:
        first_node = {}
        current = first_node

        for index, (item_id, model_path) in enumerate(data_entries):
            if fallback_item == "fishing_rod":
                on_true = handle_fishing_rod_cast(item_id, model_path)
            elif fallback_item == "bow":
                on_true = handle_bow_pull(item_id, model_path)
            else:
                on_true = {
                    "model": f"skyblock:skyblock/{model_path}",
                    "type": "model"
                }

            node = {
                "predicate": "custom_data",
                "property": "component",
                "type": "condition",
                "value": {"id": item_id},
                "on_true": on_true,
                "on_false": fallback if index == len(data_entries) - 1 else {}
            }

            current.update(node)
            current = node["on_false"]

        fallback = first_node

    if name_cases:
        result["model"] = {
            "cases": name_cases,
            "component": "custom_name",
            "fallback": fallback,
            "property": "component",
            "type": "select"
        }
    else:
        result["model"] = fallback

    return result


# === Texturen & Modelle erzeugen ===
def create_referenced_model(target_root, model_path, parent="item/handheld"):
    out_path = get_model_path(target_root, model_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if parent is None:
        parent = "item/handheld"

    if not os.path.exists(out_path):
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({
                "parent": f"skyblock:{parent}",
                "textures": {"layer0": f"skyblock:skyblock/{model_path}"}
            }, f, indent=2)


def copy_texture(texture_src, target_root, model_path):
    texture_out = get_texture_path(target_root, model_path)
    os.makedirs(os.path.dirname(texture_out), exist_ok=True)

    # Nur den Dateinamen holen (ohne Verzeichnisse)
    filename = os.path.basename(model_path) + ".png"

    # Rekursiv nach der Datei suchen
    found_png = None
    for root, _, files in os.walk(texture_src):
        if filename in files:
            found_png = os.path.join(root, filename)
            break

    # Fallback auf default.png, falls nicht gefunden
    if not found_png:
        log_warning(f"Das Bild '{filename}' wurde nicht gefunden. Fallback auf 'default.png'.")
        found_png = os.path.join(texture_src, "default.png")

    found_mcmeta = found_png + ".mcmeta"

    # Kopieren
    shutil.copy2(found_png, texture_out)
    if os.path.exists(found_mcmeta):
        shutil.copy2(found_mcmeta, texture_out + ".mcmeta")


# === Hauptfunktion ===
def generate_files(data, cfg):
    target_root = cfg["target"]
    texture_src = cfg["textures"]

    for item_name, (type_prefix, entries) in data.items():
        model_data = build_model_structure(entries, item_name, type_prefix)

        # Hauptmodell
        main_model_path = get_main_model_path(target_root, item_name)
        os.makedirs(os.path.dirname(main_model_path), exist_ok=True)

        with open(main_model_path, "w", encoding="utf-8") as f:
            json.dump(model_data, f, indent=2)
        print(f"Modell gespeichert: {item_name}")

        for _, model_path, parent in entries:
            if not model_path:
                continue
            if parent is not None:
                parent = "item/" + parent
            create_referenced_model(target_root, model_path, parent)
            copy_texture(texture_src, target_root, model_path)

            # === Sonderfall für items mit mehreren texturen
            if item_name == "bow" or item_name == "fishing_rod":
                generate_variant_models(model_path, parent, texture_src, target_root)


def prepare_texturepack(cfg):
    resources_path = cfg.get("resources")
    target_root = cfg.get("target")
    parent_dir = cfg.get("parents")

    if not resources_path or not target_root or not parent_dir:
        raise ValueError("Config muss 'resources', 'target' und 'parent' enthalten.")

    # 1. Ressourcen-Ordner komplett nach target kopieren (rekursiv)
    if os.path.exists(target_root):
        shutil.rmtree(target_root)
    shutil.copytree(resources_path, target_root)

    # 2. Parent-Ordnerinhalt nach target/assets/skyblock/models/item kopieren
    target_parent_dir = os.path.join(target_root, "assets", "skyblock", "models", "item")
    os.makedirs(target_parent_dir, exist_ok=True)

    if not os.path.isdir(parent_dir):
        raise FileNotFoundError(f"Parent-Ordner nicht gefunden: {parent_dir}")

    # Alle Dateien und Unterordner rekursiv kopieren
    for entry in os.listdir(parent_dir):
        src_path = os.path.join(parent_dir, entry)
        dst_path = os.path.join(target_parent_dir, entry)

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


def generate_variant_models(base_model_path, parent, texture_src, target_root):
    """
    Erstellt Modell- und Texturdateien für alle Varianten, die den base_filename enthalten.

    :param base_model_path: z.B. "weapons/bows/mosquito_bow"
    :param parent: z.B. "item/bow"
    :param texture_src: Pfad zum Texturen-Ordner
    :param target_root: Zielpfad für Modelle und Texturen
    """
    base_filename = os.path.basename(base_model_path)

    for root, _, files in os.walk(texture_src):
        for file in files:
            if not file.endswith(".png"):
                continue
            if base_filename not in file:
                continue

            texture_name = file[:-4]  # ohne ".png"
            model_name = f"{os.path.dirname(base_model_path)}/{texture_name}" if "/" in base_model_path else texture_name

            create_referenced_model(target_root, model_name, parent)
            copy_texture(texture_src, target_root, model_name)