# parser.py
import os
import re
from log import log_info, log_warning, reset_log

armor_pieces = {
    "helmet": "HELMET",
    "chestplate": "CHESTPLATE",
    "leggings": "LEGGINGS",
    "boots": "BOOTS"
}

armor_types = [
    "leather",
    "iron",
    "golden",
    "chainmail",
    "diamond"
]


def parse_input_files(config):
    """Hauptfunktion zum Parsen aller .dat-Dateien aus dem definierten Verzeichnis."""
    model_definitions = config.get("model_definitions")
    if not model_definitions:
        log_warning("Pfad zu 'model_definitions' fehlt in der Konfiguration.")
        return

    result = {}
    seen_definitions = {}  # name -> list of (file, line)
    reset_log()

    for filename in os.listdir(model_definitions):
        if not filename.endswith(".dat"):
            continue

        filepath = os.path.join(model_definitions, filename)
        parsed = _parse_single_file(filepath, filename)
        _merge_parsed_data(result, seen_definitions, parsed)

        # 💡 armor_set direkt nach dem Parsen verarbeiten
        for type_prefix, name, entries, _, _ in parsed:
            if name == "armor_set":
                for (set_name, base_path, _) in entries:
                    parse_armor_set(config.get("textures"), result, seen_definitions, set_name, base_path)

    result.pop("armor_set", None)
    return result


def _parse_single_file(filepath, filename):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parsed_data = []

    for match in re.finditer(r'(?:\b(\w+)\s+)?(\w+)\s*{([^}]*)}', content, re.MULTILINE | re.DOTALL):
        type_prefix, name, block_content = match.groups()
        if not type_prefix:
            type_prefix = "item"

        line_number = content[:match.start()].count('\n') + 1

        entries = []
        for line in block_content.strip().splitlines():
            line = line.strip().strip('"')
            if not line or line.startswith("#"):
                continue
            parts = [p.strip().strip('"') for p in line.split(',')]
            if len(parts) == 2:
                entries.append((parts[0], parts[1], None))
            elif len(parts) == 3:
                entries.append((parts[0], parts[1], parts[2]))

        parsed_data.append((type_prefix, name, entries, filename, line_number))

    return parsed_data


def _merge_parsed_data(result, seen_definitions, parsed_data):
    for type_prefix, name, entries, filename, line_number in parsed_data:
        if name not in result:
            result[name] = (type_prefix, entries)  # type_prefix mit speichern
            seen_definitions[name] = [(filename, line_number)]
        else:
            seen_definitions[name].append((filename, line_number))
            log_info(f"Doppelte Deklaration von '{name}' in {filename}:{line_number}")

            # Einträge anhängen (in Tuple an Index 1)
            result[name] = (
                result[name][0],  # type_prefix bleibt gleich
                result[name][1] + entries
            )


def parse_armor_set(texture_src, model_data, seen_definitions, set_name, base_path):
    for armor_type in armor_types:
        for piece_suffix, piece_upper in armor_pieces.items():
            file_name = f"{base_path}_{piece_suffix}.png"
            file_name_only = os.path.basename(file_name)

            found = False
            for root, _, files in os.walk(texture_src):
                if file_name_only in files:
                    found = True
                    break

            if not found:
                continue

            id_key = f"{set_name}_{piece_upper}"
            texture_path = f"{base_path}_{piece_suffix}"

            key = f"{armor_type}_{piece_suffix}"

            if key not in model_data:
                model_data[key] = ("item", [(id_key, texture_path, None)])
                seen_definitions[key] = [("armor_set_generated", 0)]  # Hier Quelle reinpacken
            else:
                type_prefix, entries = model_data[key]
                entries.append((id_key, texture_path, None))
                model_data[key] = (type_prefix, entries)
