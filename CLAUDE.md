# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fala-Texto is a healthcare speech-to-text documentation system targeting clinical environments. It transcribes doctors' voice notes into structured text, auto-populates PDF forms, and validates clinical terminology in real-time.

The preferred production stack is the **Kotlin Android app** communicating with the **FastAPI transcription backend**. The Kivy/Python app is a legacy prototype.

## Repository Structure

- `App-Kotlin/VoiceSurgeryWhisper/` — Primary Android app (Kotlin + Retrofit2 + Jetpack)
- `App-Kotlin/VoiceSurgeryGoogleAPI/` — Alternative using Android's built-in SpeechRecognizer
- `servico-transcricao/backend/` — Primary backend (FastAPI + OpenAI Whisper "turbo" + GPU)
- `servico-transcricao/API/` — Legacy Flask backend (kept for reference)
- `Fine-Tuning/` — Scripts to fine-tune Whisper on Portuguese clinical data
- `App-kivy/` — Legacy Python/Kivy Android prototype

## Backend (FastAPI)

```bash
cd servico-transcricao/backend
pip install -r requirements.txt
uvicorn servico:app --host 0.0.0.0 --port 3050
```

**Docker (production):**
```bash
docker build -t transcricao-api .
docker run -d -p 3050:3050 --restart always -m 6g --gpus all \
  -v /path/to/volume:/app/imagens transcricao-api
```

The Nginx reverse proxy config lives at `servico-transcricao/backend/processarpdffalatex.zapto.org.conf`.

## Android App (Kotlin)

```bash
cd App-Kotlin/VoiceSurgeryWhisper
./gradlew assembleDebug        # Build debug APK
./gradlew assembleRelease      # Build release APK
./gradlew installDebug         # Install on connected device/emulator
./gradlew test                 # Unit tests
./gradlew connectedAndroidTest # Instrumented tests
```

- minSdk 28, targetSdk 36, Kotlin JVM target 11
- JVM heap set to 2 GB in `gradle.properties`

## Fine-Tuning

```bash
cd Fine-Tuning
pip install -r requirements.txt
python Transformers.py    # Train Whisper on clinical dataset
python Avaliarmodelo.py   # Evaluate with WER metric
```

## Architecture

```
Android App (Kotlin)
  └── AudioRecorder.kt          records audio
  └── network/ (Retrofit2)      POST audio to FastAPI
  └── ui/PdfFlowManager.kt      renders and navigates PDF forms
  └── viewmodel/QuizStateManager.kt  manages answer state

FastAPI Service (servico-transcricao/backend/servico.py)
  └── Audio preprocessing       librosa + noisereduce + pydub
  └── Whisper "turbo"           speech-to-text (GPU/CUDA)
  └── Text normalization        clinical terminology mapping
  └── PyMuPDF (fitz)            PDF form extraction and population
  └── JWT auth                  fastapi-jwt-auth
  └── Rate limiting             slowapi
  └── DeepFace/FaceNet          optional face verification
```

The mobile app authenticates with JWT, sends raw audio, and receives transcribed + normalized text that is used to fill form fields.

## Key Files

| File | Purpose |
|------|---------|
| `servico-transcricao/backend/servico.py` | Entire backend logic (~624 lines) |
| `App-Kotlin/VoiceSurgeryWhisper/app/src/main/java/…/services/AudioRecorder.kt` | Microphone capture |
| `App-Kotlin/VoiceSurgeryWhisper/app/src/main/java/…/network/` | Retrofit API definitions |
| `App-Kotlin/VoiceSurgeryWhisper/app/src/main/java/…/data/AuthRepository.kt` | JWT auth flow |
| `App-Kotlin/VoiceSurgeryWhisper/app/src/main/java/…/ui/PdfFlowManager.kt` | PDF form rendering |
| `Fine-Tuning/Transformers.py` | Whisper fine-tuning script |
