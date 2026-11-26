
import json
from pathlib import Path

# Locate the storyboard file in the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORYBOARD_FILE = PROJECT_ROOT / "storyboard.json"


def read_storyboard():
    if not STORYBOARD_FILE.exists():
        print("ERROR: storyboard.json was not found.")
        return

    # Read JSON data
    with open(STORYBOARD_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Get project information
    project = data.get("project", {})
    title = project.get("title", data.get("title", "Untitled Film"))

    # Get scenes
    shots = data.get("shots", [])

    if not isinstance(shots, list) or not shots:
        print("ERROR: No valid shots found.")
        return

    print("=" * 50)
    print("ETHIOPIAN HERITAGE FILM")
    print("=" * 50)

    print(f"Film title: {title}")
    print(f"Number of scenes: {len(shots)}")
    print("\nSCENES:")

    total_duration = 0

    for shot in shots:
        scene_id = shot.get("id", "Unknown")
        scene_title = shot.get("title", "Untitled")
        duration = shot.get("duration_seconds", 0)

        total_duration += duration

        print(f"{scene_id}: {scene_title} - {duration} seconds")

    # Include end card duration
    end_card = data.get("end_card", {})
    end_card_duration = end_card.get("duration_seconds", 0)

    total_duration += end_card_duration

    print("\n" + "=" * 50)
    print(f"Scenes duration: {total_duration - end_card_duration} seconds")
    print(f"End card duration: {end_card_duration} seconds")
    print(f"TOTAL FILM DURATION: {total_duration} seconds")
    print("=" * 50)


if __name__ == "__main__":
    read_storyboard()
