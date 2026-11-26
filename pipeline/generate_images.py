
import os
import json
import base64
import argparse
from pathlib import Path

import requests
from dotenv import load_dotenv


# Project configuration
ROOT = Path(__file__).resolve().parent.parent
STORYBOARD = ROOT / "storyboard.json"
OUTPUT_DIR = ROOT / "outputs" / "images"

MODEL = "@cf/black-forest-labs/flux-1-schnell"

load_dotenv(ROOT / ".env")


def generate_image(scene_id, force=False):

    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")

    if not account_id or not api_token:
        raise ValueError("Cloudflare credentials are missing.")

    # Read storyboard
    with open(STORYBOARD, "r", encoding="utf-8") as file:
        storyboard = json.load(file)

    shots = storyboard.get("shots", [])

    scene = next(
        (shot for shot in shots if shot.get("id") == scene_id),
        None
    )

    if scene is None:
        raise ValueError(f"Scene not found: {scene_id}")

    prompt = scene.get("image_prompt")

    if not prompt:
        raise ValueError(f"Image prompt missing: {scene_id}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / f"{scene_id}.jpg"

    # Cache existing images
    if output_file.exists() and not force:
        print(f"SKIPPED: {output_file.name} already exists.")
        return

    # Cloudflare API endpoint
    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{account_id}/ai/run/{MODEL}"
    )

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "steps": 4
    }

    print("=" * 50)
    print(f"Generating image: {scene_id}")
    print(f"Model: {MODEL}")
    print("Sending request to Cloudflare...")
    print("=" * 50)

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=180
    )

    # Check API response
    if not response.ok:
        try:
            error_data = response.json()
        except ValueError:
            error_data = response.text

        raise RuntimeError(
            f"Cloudflare API error ({response.status_code}): "
            f"{error_data}"
        )

    data = response.json()

    if not data.get("success", False):
        raise RuntimeError(
            f"Cloudflare returned an error: {data.get('errors')}"
        )

    image_base64 = data.get("result", {}).get("image")

    if not image_base64:
        raise RuntimeError("No image was returned by Cloudflare.")

    # Decode and save JPEG
    image_bytes = base64.b64decode(image_base64)

    output_file.write_bytes(image_bytes)

    print("SUCCESS: Image generated!")
    print(f"Saved to: {output_file}")
    print("=" * 50)



def generate_all(force=False):

    with open(STORYBOARD, "r", encoding="utf-8") as file:
        storyboard = json.load(file)

    shots = storyboard.get("shots", [])

    successful = []
    failed = []

    print("\nSTARTING AUTOMATIC IMAGE GENERATION")
    print(f"Total scenes: {len(shots)}")
    print("=" * 50)

    for scene in shots:
        scene_id = scene.get("id")

        try:
            generate_image(scene_id, force)
            successful.append(scene_id)

        except Exception as error:
            print(f"FAILED: {scene_id} - {error}")
            failed.append(scene_id)

    print("\nIMAGE GENERATION REPORT")
    print("=" * 50)
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("Failed scenes:", ", ".join(failed))

    print("=" * 50)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("scene_id", nargs="?", default=None)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--force", action="store_true")

    args = parser.parse_args()

    try:
        if args.all:
            generate_all(args.force)

        elif args.scene_id:
            generate_image(args.scene_id, args.force)

        else:
            parser.print_help()

    except Exception as error:
        print(f"ERROR: {error}")
