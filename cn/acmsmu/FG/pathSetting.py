from pathlib import Path

DATA_PATH = Path(__file__).parent / "data"
ASSERT_PATH = DATA_PATH / "assets"

IMAGE_PATH = ASSERT_PATH / "images"
WC_PATH = ASSERT_PATH / "wc"
GROUP_DATA_PATH = ASSERT_PATH / "group"

IMAGE_PATH.mkdir(parents=True, exist_ok=True)
WC_PATH.mkdir(parents=True, exist_ok=True)
GROUP_DATA_PATH.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = DATA_PATH / "config.json"
if not CONFIG_FILE.exists():
    import json
    from .defaultData import DEFAULT_CONFIG

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            DEFAULT_CONFIG,
            f,
            ensure_ascii=False,
            indent=4,
        )