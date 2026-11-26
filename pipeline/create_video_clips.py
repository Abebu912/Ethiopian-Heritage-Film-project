
import json
import subprocess
from pathlib import Path
import argparse


ROOT = Path(__file__).resolve().parent.parent

STORYBOARD = ROOT / "storyboard.json"
IMAGE_DIR = ROOT / "outputs" / "images"
VIDEO_DIR = ROOT / "outputs" / "videos"

FPS = 24
WIDTH = 1080
HEIGHT = 1920


def create_clip(scene, force=False):

    scene_id = scene["id"]
    duration = scene.get("duration_seconds", 8)

    image_file = IMAGE_DIR / f"{scene_id}.jpg"
    video_file = VIDEO_DIR / f"{scene_id}.mp4"

    if not image_file.exists():
        raise FileNotFoundError(
            f"Image not found: {image_file}"
        )

    if video_file.exists() and not force:
        print(f"SKIPPED: {video_file.name} already exists.")
        return

    frames = int(duration * FPS)

    # Slow zoom effect
    video_filter = (
        f"scale={WIDTH}:{HEIGHT}:"
        "force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"zoompan=z='min(zoom+0.0005,1.08)':"
        "x='iw/2-(iw/zoom/2)':"
        "y='ih/2-(ih/zoom/2)':"
        f"d={frames}:"
        f"s={WIDTH}x{HEIGHT}:"
        f"fps={FPS},"
        "format=yuv420p"
    )

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-framerate", str(FPS),
        "-i", str(image_file),
        "-vf", video_filter,
        "-frames:v", str(frames),
        "-an",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(video_file)
    ]

    print(f"\nCreating video: {scene_id}")
    print(f"Duration: {duration} seconds")

    subprocess.run(
        command,
        check=True
    )

    print(f"SUCCESS: {video_file.name}")


def create_all(force=False):

    with open(STORYBOARD, "r", encoding="utf-8") as file:
        storyboard = json.load(file)

    shots = storyboard.get("shots", [])

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    successful = []
    failed = []

    print("\nSTARTING VIDEO CLIP GENERATION")
    print(f"Total scenes: {len(shots)}")

    for scene in shots:

        scene_id = scene.get("id", "unknown")

        try:
            create_clip(scene, force)
            successful.append(scene_id)

        except Exception as error:
            print(f"FAILED: {scene_id}: {error}")
            failed.append(scene_id)

    print("\nVIDEO GENERATION REPORT")
    print("=" * 45)
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("Failed scenes:", ", ".join(failed))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--all",
        action="store_true"
    )

    parser.add_argument(
        "--force",
        action="store_true"
    )

    args = parser.parse_args()

    if args.all:
        create_all(args.force)
    else:
        parser.print_help()
