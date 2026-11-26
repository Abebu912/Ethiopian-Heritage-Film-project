# Ethiopia: A Living Heritage 🇪🇹

An AI-powered short documentary celebrating Ethiopia's cultural heritage, traditions, landscapes, food, music, and hospitality.

## 1. Project Overview

**Project Title:** Ethiopia: A Living Heritage  
**Amharic Title:** ኢትዮጵያ፦ ሕያው ቅርስ  
**Duration:** Approximately 67 seconds  
**Narration:** Amharic  
**Subtitles:** English  
**Formats:** Horizontal (16:9) and Vertical (9:16)

This project uses AI-assisted content generation and video production techniques to present Ethiopian cultural heritage through eight documentary scenes.

## 2. Project Objectives

- Celebrate Ethiopian history, traditions, and cultural identity.
- Present Ethiopian landscapes, coffee ceremonies, traditional food, clothing, music, and hospitality.
- Explore AI-assisted multimedia production.
- Create accessible cultural content using Amharic narration and English subtitles.

## 3. Technologies and Tools

- Python – Pipeline development and automation.
- Cloudflare Workers AI – Image generation.
- Google Gemini TTS – Amharic narration generation.
- ACE-Step 1.5 – Original instrumental music generation.
- FFmpeg – Video editing, scene assembly, audio mixing, and subtitles.
- Git and GitHub – Version control and project hosting.

## 4. Project Structure

```text
Ethiopian-Heritage-Film/
├── pipeline/
│   ├── assemble_film.py
│   ├── create_video_clips.py
│   ├── generate_images.py
│   ├── generate_narration.py
│   ├── read_storyboard.py
│   └── validate_storyboard.py
├── outputs/
│   ├── images/
│   ├── videos/
│   ├── audio/
│   │   ├── music/
│   │   └── narration/
│   └── final/
├── storyboard.json
├── .gitignore
└── README.md
```

## 5. Documentary Scenes

The film contains eight scenes:

1. Ethiopian highlands at sunrise.
2. Traditional Ethiopian coffee ceremony.
3. Injera and shared Ethiopian food.
4. Traditional Ethiopian clothing.
5. Ethiopian traditional music and dance.
6. Ethiopian hospitality and community.
7. Historic rock-hewn churches of Lalibela.
8. Ethiopian highlands at sunset.

## 6. Final Outputs

- `ethiopia_heritage_horizontal.mp4` – Horizontal documentary.
- `ethiopia_heritage_vertical.mp4` – Vertical documentary.
- `subtitles.srt` – English subtitle file.

Generated images, individual scene clips, narration recordings, and original music are organized in the `outputs/` directory.

## 7. Production Workflow

1. Define the documentary storyboard in JSON.
2. Generate visual assets using AI.
3. Create scene clips using FFmpeg with pan-and-zoom motion.
4. Generate Amharic narration using Gemini TTS.
5. Generate original instrumental background music using ACE-Step 1.5.
6. Assemble scenes, narration, subtitles, and music using FFmpeg.
7. Export horizontal and vertical documentary versions.
8. Review the final outputs.

**Production note:** Scene motion was created from generated still images using FFmpeg pan-and-zoom effects. The project does not claim to use AI-generated Wan 2.2 motion footage.

## 8. Setup Requirements

- Python 3
- FFmpeg
- Git
- Required Python packages and API credentials for the selected generation services

Keep API credentials in a local `.env` file. Never upload `.env` or expose API keys publicly.

## 9. Ethical Considerations

This documentary explores Ethiopian culture respectfully. AI-generated images, narration, and music should be clearly disclosed. Cultural representations should be reviewed for accuracy, and real people's likenesses or voices should only be used with appropriate permission.

## 10. Repository

**GitHub:** https://github.com/Abebu912/Ethiopian-Heritage-Film-project

## 11. Project Purpose

This project demonstrates how AI-assisted creative technologies and software engineering can be combined to produce an educational and culturally meaningful documentary about Ethiopia.

**Created for:** 10 Academy – AI-Content Generation: The Heritage Short Challenge.