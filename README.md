# Skyblock Texture Generator

> ⚠️ **Disclaimer**: I do **not** own the rights to most of the textures or images used with this project. All assets belong to their respective creators and are used here purely for personal or illustrative purposes.

---
This Tool can generate with low effort a complete Texturepack for Hypixel Skyblock.

---

## 🛠️ Overview
The Program reads `.dat` from the model_definitions folder. 
Each declaration defines how a Minecraft item or block ID should map to a texture and optional rendering options.
It collects all Informations and creates a Texturepack that is saved in the target location of the config.

---

## 📝 Syntax

Each `.dat` file contains one or more block-style declarations in the following format:

```plaintext
[type] <minecraft_id> {
    <skyblock_id>, <path/in/texturepack>[, <render_option_from_render_parent>]
}

or

[type] <minecraft_id> {
    <color>:<item_name>, <path/in/texturepack>[, <render_option_from_render_parent>]
}
```

Element Descriptions:
 * [type] (optional):
    Use block if the ID represents a block instead of an item. If omitted, item is assumed by default.
 * <minecraft_id>:
    The Minecraft item ID (e.g. iron_sword, gold_block, leather_chestplate).
 * <skyblock_id>:
    The identifier used in Skyblock (e.g. WISE_WITHER_SWORD).
 * <color>:<item_name> (alternative to <skyblock_id>):
    Used when matching by display name and color instead of item ID.
    Example: green:Sell — matches items named "Sell" in green.
 * <path/in/texturepack>:
    Relative path to the texture (excluding the .png extension), e.g. weapons/swords/daedalus_blade.
 * <render_option_from_render_parent> (optional):
    Refers to a render option defined in render_parent (e.g. "giant_ui" or "handheld_staff"). handheld is chosen by default.

### Syntax Example
```plaintext
diamond_sword {
ASPECT_OF_THE_END, weapons/swords/aspect_of_the_end
}

paper {
green:View Graphs, ui/bazaar/view_graph
gold:Create Sell Offer, ui/bazaar/open_chest_outgoing_yellow
}
```

---
## Examples
### 🔄 Type Prefix: block or item

By default, everything is assumed to be an item.
If the ID refers to a block prepend the type prefix:

```plaintext
block crafting_table {
green:Crafting Table, ui/menu/crafting
}
```

## 🎨 Render Options
Optionally, you can include a render option as a third value. 
This must refer to a .json from your render_parent directory.
```plaintext
ender_pearl {
SPIRIT_LEAP, items/dungeons/spirit_leap, giant_ui
}
```

## 👕 Armor Sets
Armor sets can be declared using a special armor_set keyword:
```plaintext
armor_set {
WISE_WITHER, armor/storm/storm
}
```

This will automatically generate model entries for each piece and type:

    leather_helmet → storm_HELMET, armor/storm_helmet.png

    leather_chestplate → storm_CHESTPLATE, armor/storm_chestplate.png

    ... and so on

The parser scans your texture folder and only includes files that actually exist.
These entries are generated for all five vanilla armor types:

    leather, iron, golden, chainmail, diamond

And for all four armor slots:

    helmet, chestplate, leggings, boots

## 🔍 Advanced: Name-Based Selection

Instead of mapping by Skyblock ID, you can also target item names with color selectors:
```plaintext
gold_ore {
green:Advanced Mode, ui/bazaar/computer_graph
}
```

This creates a condition that applies to any item named Advanced Mode with green text (§a).

Name selectors follow this format:
```plaintext
<color>:<display name>
```

Valid Minecraft colors are: white, gray, dark_gray, black, red, dark_red, gold, yellow, green, dark_green, aqua, dark_aqua, blue, dark_blue, light_purple, dark_purple.
