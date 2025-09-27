# 🎙️ Podcast Transcriber & Analyzer

Transkribiere YouTube-Podcasts automatisch und extrahiere die wichtigsten Insights mit KI.

## 🚀 Schnellstart mit GitHub Codespaces

### 1. Codespace starten
- Klicke auf den grünen **"Code"** Button
- Wähle **"Codespaces"** Tab
- Klicke **"Create codespace on main"**

### 2. API Keys setzen
Im Terminal des Codespace:
```bash
export OPENAI_API_KEY="dein-openai-key"
export ANTHROPIC_API_KEY="dein-anthropic-key"
```

### 3. App starten
```bash
python app.py
```

Die App läuft dann auf Port 5000 und öffnet sich automatisch!

## 💻 Lokale Installation

### Voraussetzungen
- Python 3.8+
- FFmpeg
- OpenAI API Key
- Anthropic API Key (optional)

### Installation
```bash
# Repository klonen
git clone https://github.com/DEIN-USERNAME/podcast-transcriber.git
cd podcast-transcriber

# FFmpeg installieren (macOS)
brew install ffmpeg

# FFmpeg installieren (Ubuntu/Debian)
sudo apt-get install ffmpeg

# FFmpeg installieren (Windows)
# Download von https://ffmpeg.org/download.html

# Python-Pakete installieren
pip install -r requirements.txt

# Umgebungsvariablen setzen
export OPENAI_API_KEY="dein-key"
export ANTHROPIC_API_KEY="dein-key"

# App starten
python app.py
```

## 🔑 API Keys

### OpenAI
1. Gehe zu [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Erstelle einen neuen API Key
3. Füge Guthaben hinzu (Whisper kostet ~$0.006/Minute)

### Anthropic (optional)
1. Gehe zu [console.anthropic.com](https://console.anthropic.com)
2. Erstelle einen API Key
3. Claude Haiku für günstige Analysen

## 📖 Nutzung

1. **YouTube URL eingeben**: Füge die URL eines YouTube-Videos ein
2. **Modell wählen**: Claude (Haiku) oder GPT-4o-mini für Analyse
3. **Optionen**:
   - **"Transkribieren & Analysieren"**: Vollständiger Workflow
   - **"Nur Transkribieren"**: Nur das Transkript erstellen
4. **Ergebnisse**: Transkript und Key Insights werden angezeigt

## 💰 Kosten

- **Transkription**: ~$0.36 für 60 Minuten (OpenAI Whisper)
- **Analyse**: ~$0.10-0.20 pro Podcast (GPT-4o-mini oder Claude Haiku)
- **Gesamt**: ~$0.50 pro Podcast-Episode

## 🐛 Fehlerbehebung

### "FFmpeg nicht gefunden"
- Stelle sicher, dass FFmpeg installiert ist
- In Codespaces wird es automatisch installiert

### "API Key fehlt"
- Setze die Umgebungsvariablen korrekt
- In Codespaces: Nutze Secrets (Settings → Secrets → Codespaces)

### "Transkription fehlgeschlagen"
- Überprüfe dein OpenAI-Guthaben
- Stelle sicher, dass die YouTube-URL gültig ist

## 📝 Lizenz

MIT License
