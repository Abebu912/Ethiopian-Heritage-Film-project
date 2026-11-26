
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORYBOARD_FILE = PROJECT_ROOT / "storyboard.json"


def validate_storyboard():
    with open(STORYBOARD_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    errors = []

    # Check scenes
    shots = data.get("shots")

    if not isinstance(shots, list) or not shots:
        print("FAILED: No scenes found.")
        return

    required_fields = [
        "id",
        "title",
        "duration_seconds",
        "image_prompt",
        "motion_prompt",
        "narration_am",
        "subtitle_en"
    ]

    scene_ids = set()
    total_duration = 0

    for index, shot in enumerate(shots, start=1):

        # Check required fields
        for field in required_fields:
            if not shot.get(field):
                errors.append(
                    f"Scene {index}: Missing {field}"
                )

        # Check duplicate IDs
        scene_id = shot.get("id")

        if scene_id in scene_ids:
            errors.append(
                f"Duplicate scene ID: {scene_id}"
            )
        scene_ids.add(scene_id)

        # Check duration
        duration = shot.get("duration_seconds")

        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
            errors.append(
                f"Scene {index}: Invalid duration"
            )
        else:
            total_duration += duration

    # Check end card
    end_card = data.get("end_card", {})
    end_duration = end_card.get("duration_seconds", 0)

    if not isinstance(end_duration, (int, float)) or isinstance(end_duration, bool) or end_duration <= 0:
        errors.append("Invalid end card duration.")
        end_duration = 0

    total_duration += end_duration

    # Display results
    print("=" * 45)
    print("STORYBOARD VALIDATION REPORT")
    print("=" * 45)

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print("[ERROR]", error)
    else:
        print("[SUCCESS] All required fields exist.")
        print("[SUCCESS] Scene IDs are unique.")
        print("[SUCCESS] All durations are valid.")
        print("[SUCCESS] End card is valid.")

    print(f"\nTotal scenes: {len(shots)}")
    print(f"Total duration: {total_duration} seconds")

    if 60 <= total_duration <= 90:
        print("[SUCCESS] Film duration is within 60-90 seconds.")
    else:
        print("[WARNING] Film duration is outside 60-90 seconds.")

    print("=" * 45)


if __name__ == "__main__":
    validate_storyboard()
