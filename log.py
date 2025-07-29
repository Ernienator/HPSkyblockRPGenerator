import os

LOG_FILE = "logs/log.txt"


def ensure_log_dir():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def reset_log():
    ensure_log_dir()
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("")


def log_info(message):
    ensure_log_dir()
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[INFO] {message}\n")


def log_warning(message):
    ensure_log_dir()
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[WARNING] {message}\n")
