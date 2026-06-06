import json
import os
from pathlib import Path
from fastapi import APIRouter, Depends
from routers.auth import get_current_user
from config import TEMPLATES_DIR

router = APIRouter(prefix="/api/v1", tags=["templates"])

# In-memory template cache, loaded at startup
TEMPLATES: dict[str, dict] = {}


def load_templates():
    """Read all .json files from the templates directory into memory."""
    global TEMPLATES
    TEMPLATES.clear()
    folder = Path(TEMPLATES_DIR)
    if not folder.exists():
        os.makedirs(folder, exist_ok=True)
        return
    for f in sorted(folder.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            TEMPLATES[f.stem] = data
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Skipping invalid template {f.name}: {e}")
    print(f"Loaded {len(TEMPLATES)} templates from {TEMPLATES_DIR}")


@router.get("/templates")
def list_templates(current_user=Depends(get_current_user)):
    """Return all loaded templates as a list with key, name, category, and icon."""
    return [
        {
            "key": key,
            "name": t.get("name", key),
            "category": t.get("category", "other"),
            "icon": t.get("icon", "file"),
            "description": t.get("description", ""),
        }
        for key, t in TEMPLATES.items()
    ]
