
import json
import subprocess
from pathlib import Path

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

ROOT = Path(__file__).resolve().parent.parent
STORYBOARD = ROOT / "storyboard.json"
OUTPUT_DIR = ROOT / "outputs" / "final"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(STORYBOARD, "r", encoding="utf-8") as file:
    data = json.load(file)

shots = data["shots"]
scene_count = len(shots)

video_files = [
    ROOT / "outputs" / "videos" / f"scene_{i:02d}.mp4"
    for i in range(1, scene_count + 1)
]

narration_files = [
    ROOT / "outputs" / "audio" / "narration" / f"scene_{i:02d}.wav"
    for i in range(1, scene_count + 1)
]

music_file = (
    ROOT / "outputs" / "audio" / "music" /
    "ethiopian_heritage_music.mp3"
)

end_card_duration = int(data["end_card"]["duration_seconds"])

scene_duration = sum(
    int(shot["duration_seconds"]) for shot in shots
)

total_duration = scene_duration + end_card_duration


# ==========================================
# 2. CHECK REQUIRED FILES
# ==========================================

required_files = video_files + narration_files + [music_file]

missing_files = [
    str(path) for path in required_files if not path.exists()
]

if missing_files:
    print("\nERROR: Missing production files:")

    for path in missing_files:
        print(" -", path)

    raise SystemExit(1)

print("\nAll production files verified.")
print(f"Number of scenes: {scene_count}")
print(f"Film duration: {total_duration} seconds")


# ==========================================
# 3. SUBTITLE GENERATION
# ==========================================

def create_subtitles():

    subtitle_file = OUTPUT_DIR / "subtitles.srt"

    def timestamp(seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        return f"{hours:02}:{minutes:02}:{secs:02},000"

    current_time = 0

    with open(subtitle_file, "w", encoding="utf-8") as srt:

        for index, shot in enumerate(shots, start=1):

            duration = int(shot["duration_seconds"])

            start = current_time
            end = current_time + duration

            subtitle = shot["subtitle_en"].strip()

            srt.write(f"{index}\n")
            srt.write(
                f"{timestamp(start)} --> {timestamp(end)}\n"
            )
            srt.write(subtitle + "\n\n")

            current_time = end

    print("English subtitles created.")

    return subtitle_file


# ==========================================
# 4. VIDEO ASSEMBLY FUNCTION
# ==========================================

def run_ffmpeg(width, height, output_name):

    print(f"\nCreating {output_name}...")

    command = ["ffmpeg", "-y"]

    # Add eight video inputs
    for path in video_files:
        command += ["-i", str(path)]

    # Add eight narration inputs
    for path in narration_files:
        command += ["-i", str(path)]

    # Add background music
    command += ["-i", str(music_file)]

    # Add black end card
    command += [
        "-f", "lavfi",
        "-i",
        f"color=c=black:s={width}x{height}:r=30:d={end_card_duration}"
    ]

    filters = []

    # --------------------------------------
    # 4.1 NORMALIZE VIDEO SCENES
    # --------------------------------------

    for i, shot in enumerate(shots):

        duration = int(shot["duration_seconds"])

        filters.append(
            f"[{i}:v]"
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            "fps=30,"
            "setsar=1,"
            "format=yuv420p,"
            f"trim=duration={duration},"
            "setpts=PTS-STARTPTS"
            f"[v{i}]"
        )

    # Join all eight video scenes
    video_labels = "".join(
        f"[v{i}]" for i in range(scene_count)
    )

    filters.append(
        f"{video_labels}"
        f"concat=n={scene_count}:v=1:a=0[vscenes]"
    )

    # --------------------------------------
    # 4.2 CREATE AI DISCLOSURE END CARD
    # --------------------------------------

    # Inputs:
    # 0-7 = videos
    # 8-15 = narration
    # 16 = music
    # 17 = black end card

    end_index = scene_count * 2 + 1

    font = "C\\:/Windows/Fonts/arial.ttf"

    filters.append(
        f"[{end_index}:v]"
        "fps=30,"
        "setsar=1,"
        "format=yuv420p,"

        f"drawtext=fontfile='{font}':"
        "text='ETHIOPIA\\: A LIVING HERITAGE':"
        f"fontcolor=white:fontsize={max(28, width // 30)}:"
        "x=(w-text_w)/2:y=h*0.38,"

        f"drawtext=fontfile='{font}':"
        "text='AI-generated visuals and music':"
        f"fontcolor=white:fontsize={max(20, width // 48)}:"
        "x=(w-text_w)/2:y=h*0.50,"

        f"drawtext=fontfile='{font}':"
        "text='Amharic narration generated with AI':"
        f"fontcolor=white:fontsize={max(18, width // 55)}:"
        "x=(w-text_w)/2:y=h*0.58"

        "[vend]"
    )

    # Join scenes and end card
    filters.append(
        "[vscenes][vend]"
        "concat=n=2:v=1:a=0[vout]"
    )

    # --------------------------------------
    # 4.3 PREPARE NARRATION
    # --------------------------------------

    for i, shot in enumerate(shots):

        narration_index = scene_count + i
        duration = int(shot["duration_seconds"])

        filters.append(
            f"[{narration_index}:a]"
            "aresample=44100,"
            "aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"apad=whole_dur={duration},"
            f"atrim=duration={duration},"
            "asetpts=PTS-STARTPTS"
            f"[a{i}]"
        )

    # Join all narration recordings
    narration_labels = "".join(
        f"[a{i}]" for i in range(scene_count)
    )

    filters.append(
        f"{narration_labels}"
        f"concat=n={scene_count}:v=0:a=1[voice]"
    )

    # --------------------------------------
    # 4.4 PAD AND SPLIT NARRATION
    # --------------------------------------

    filters.append(
        "[voice]"
        f"apad=whole_dur={total_duration},"
        f"atrim=duration={total_duration}"
        "[voicepad]"
    )

    # IMPORTANT:
    # Split the narration into two independent streams.
    # One stream is used for mixing.
    # The second controls music ducking.

    filters.append(
        "[voicepad]asplit=2"
        "[voice_mix][voice_sidechain]"
    )

    # --------------------------------------
    # 4.5 PREPARE BACKGROUND MUSIC
    # --------------------------------------

    music_index = scene_count * 2

    filters.append(
        f"[{music_index}:a]"
        "aresample=44100,"
        "aformat=sample_fmts=fltp:channel_layouts=stereo,"
        f"atrim=duration={total_duration},"
        "asetpts=PTS-STARTPTS"
        "[music]"
    )

    # --------------------------------------
    # 4.6 DUCK MUSIC UNDER NARRATION
    # --------------------------------------

    filters.append(
        "[music][voice_sidechain]"
        "sidechaincompress="
        "threshold=0.03:"
        "ratio=8:"
        "attack=20:"
        "release=500"
        "[ducked]"
    )

    # --------------------------------------
    # 4.7 MIX NARRATION AND MUSIC
    # --------------------------------------

    filters.append(
        "[voice_mix][ducked]"
        "amix=inputs=2:duration=first:weights=1 0.22,"
        "alimiter=limit=0.95"
        "[aout]"
    )

    # --------------------------------------
    # 4.8 BURN ENGLISH SUBTITLES
    # --------------------------------------

    subtitle_file = create_subtitles()

    subtitle_path = str(
        subtitle_file.resolve()
    ).replace("\\", "/")

    subtitle_path = subtitle_path.replace(":", "\\:")

    filters.append(
        f"[vout]subtitles=filename='{subtitle_path}'[vsub]"
    )

    # --------------------------------------
    # 4.9 BUILD FINAL FFMPEG COMMAND
    # --------------------------------------

    filter_complex = ";".join(filters)

    output_file = OUTPUT_DIR / output_name

    command += [
        "-filter_complex", filter_complex,

        "-map", "[vsub]",
        "-map", "[aout]",

        "-t", str(total_duration),

        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "192k",

        "-movflags", "+faststart",

        str(output_file)
    ]

    # Execute FFmpeg
    subprocess.run(command, check=True)

    print(f"\nSUCCESS: {output_file}")


# ==========================================
# 5. GENERATE BOTH VIDEO FORMATS
# ==========================================

try:

    # Horizontal video: 16:9
    run_ffmpeg(
        1920,
        1080,
        "ethiopia_heritage_horizontal.mp4"
    )

    # Vertical video: 9:16
    run_ffmpeg(
        1080,
        1920,
        "ethiopia_heritage_vertical.mp4"
    )

    print("\n====================================")
    print("FILM ASSEMBLY COMPLETED SUCCESSFULLY")
    print("====================================")

    print(f"Total duration: {total_duration} seconds")

    print("\nGenerated files:")
    print(OUTPUT_DIR / "ethiopia_heritage_horizontal.mp4")
    print(OUTPUT_DIR / "ethiopia_heritage_vertical.mp4")
    print(OUTPUT_DIR / "subtitles.srt")

except subprocess.CalledProcessError as error:

    print("\nFFMPEG ERROR:")
    print(error)

    raise SystemExit(1)
