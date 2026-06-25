from urllib.parse import urlparse
import re

def extract_folder_id_drive(url: str) -> str | None:
    parsed = urlparse(url)

    match = re.search(
        r"/folders/([a-zA-Z0-9_-]+)",
        parsed.path
    )

    return match.group(1) if match else None