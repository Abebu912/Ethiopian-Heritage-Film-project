
import os
import json
import base64
import argparse
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# Project paths
ROOT = Path(__file__).resolve().parent.parent
STORYBOARD = ROOT / "storyboard.json"
OUTPUT_DIR = ROOT / "outputs" / "audio" / "narration"

# Gemini TTS settings
MODEL = "gemini-3.8-flash-lite-tts"
VOICE = "Charon"

# Load environment variables
load_dotenv(ROOT / ".env")


def generate_narration(scene_id, force=False):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    if not STORYBOARD.exists():
        raise FileNotFoundError("storyboard.json was not found.")

    with open(STORYBOARD, "r", encoding="utf-8") as file:
        storyboard = json.load(file)

    shots = storyboard.get("shots", [])

    scene = next(
        (shot for shot in shots if shot.get("id") == scene_id),
        None
    )

    if scene is None:
        raise ValueError(f"Scene not found: {scene_id}")

    narration = scene.get("narration_am")

    if not narration:
        raise ValueError(f"Amharic narration missing: {scene_id}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / f"{scene_id}.wav"

    if output_file.exists() and not force:
        print(f"SKIPPED: {output_file.name} already exists.")
        return

    # Connect to Gemini API using v1beta
    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": "v1beta"}
    )

    print("=" * 50)
    print(f"Generating narration: {scene_id}")
    print(f"Model: {MODEL}")
    print(f"Voice: {VOICE}")
    print("=" * 50)

    # Use the Interactions API for speech generation
    interaction = client.interactions.create(
        model=MODEL,
        input=[{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": narration,
                "annotations": [{
                    "type": "speech_metadata",
                    "style": (
                        "Calm, warm, mature documentary narration. "
                        "Clear pronunciation and moderate speaking pace."
                    )
                }]
            }]
        }],
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": VOICE}
            ]
        }
    )

    # Get generated audio
    if not interaction.output_audio or not interaction.output_audio.data:
        raise RuntimeError("Gemini returned no audio data.")

    audio_data = base64.b64decode(
        interaction.output_audio.data
    )

    # Save complete WAV audio
    with open(output_file, "wb") as audio_file:
        audio_file.write(audio_data)

    print("\nSUCCESS: Narration generated!")
    print(f"Audio saved: {output_file}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "scene_id",
        help="Scene ID, for example scene_01"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate an existing audio file"
    )

    args = parser.parse_args()

    try:
        generate_narration(args.scene_id, args.force)

    except Exception as error:
        print(f"\nERROR: {error}")
        raise SystemExit(1)
