# main.py
from util import read_cfg, clear_target_folder
from parser import parse_input_files
from writer import generate_files, prepare_texturepack

if __name__ == "__main__":
    cfg_data = read_cfg("data/config.cfg")

    # Optional
    clear_target_folder(cfg_data)
    prepare_texturepack(cfg_data)

    data = parse_input_files(cfg_data)
    generate_files(data, cfg_data)
