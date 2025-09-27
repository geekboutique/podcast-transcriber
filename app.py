import os
import tempfile
import json
from flask import Flask, render_template, request, jsonify
import yt_dlp
import openai
from anthropic import Anthropic

app = Flask(__name__)

# API Keys aus Umgebungsvariablen
openai.api_key = os.getenv("OPENAI_API_KEY")
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Maximale Dateigröße für Whisper API (25MB)
MAX_FILE_SIZE = 25 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

def download_audio(youtube_url):
    """Lädt Audio von YouTube herunter"""
    try:
        temp_dir = tempfile.gettempdir()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info['title']
            duration = info['duration']
            
            audio_path = f"{temp_dir}/{title}.mp3"
            
            return {
                'path': audio_path,
                'title': title,
                'duration': duration
            }
    except Exception as e:
        raise Exception(f"Fehler beim Download: {str(e)}")

def transcribe_audio(audio_path):
    """Transkribiert Audio mit OpenAI Whisper"""
    try:
        file_size = os.path.getsize(audio_path)
        
        if file_size > MAX_FILE_SIZE:
            return transcribe_large_audio(audio_path)
        
        with open(audio_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        return transcript
    except Exception as e:
        raise Exception(f"Fehler bei Transkription: {str(e)}")

def transcribe_large_audio(audio_path):
    """Transkribiert große Audio-Dateien in Chunks"""
    try:
        from pydub import AudioSegment
        
        audio = AudioSegment.from_mp3(audio_path)
        chunk_length = 10 * 60 * 1000  # 10 Minuten
        chunks = [audio[i:i+chunk_length] for i in range(0, len(audio), chunk_length)]
        
        full_transcript = ""
        
        for i, chunk in enumerate(chunks):
            chunk_path = f"{tempfile.gettempdir()}/chunk_{i}.mp3"
            chunk.export(chunk_path, format="mp3")
            
            with open(chunk_path, "rb") as audio_file:
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            full_transcript += transcript + " "
            os.remove(chunk_path)
        
        return full_transcript
    except ImportError:
        return "Fehler: pydub nicht installiert. Bitte große Dateien vermeiden."
    except Exception as e:
        raise Exception(f"Fehler bei Chunk-Transkription: {str(e)}")

def extract_insights(transcript, use_claude=True):
    """Extrahiert Key Learnings und Insights"""
    
    prompt = """Analysiere dieses Podcast-Transkript und erstelle:

1. **Zusammenfassung** (2-3 Sätze)
2. **Top 5 Key Learnings** (Bullet Points mit konkreten Aussagen)
3. **Wichtigste Zitate/Aussagen** (3-5 markante Originalzitate)
4. **Actionable Takeaways** (Was kann der Hörer konkret umsetzen?)

Transkript:
{transcript}

Formatiere die Antwort in Markdown."""
    
    try:
        if use_claude:
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt.format(transcript=transcript[:50000])}
                ]
            )
            return response.content[0].text
        else:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Du bist ein Experte für Podcast-Analyse."},
                    {"role": "user", "content": prompt.format(transcript=transcript[:50000])}
                ],
                max_tokens=1500
            )
            return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Fehler bei Analyse: {str(e)}")

@app.route('/process', methods=['POST'])
def process_podcast():
    """Hauptendpunkt für Podcast-Verarbeitung"""
    try:
        data = request.json
        youtube_url = data.get('url')
        use_claude = data.get('use_claude', True)
        
        if not youtube_url:
            return jsonify({'error': 'Keine URL angegeben'}), 400
        
        print("Lade Audio herunter...")
        audio_info = download_audio(youtube_url)
        
        print("Transkribiere Audio...")
        transcript = transcribe_audio(audio_info['path'])
        
        print("Extrahiere Insights...")
        insights = extract_insights(transcript, use_claude)
        
        if os.path.exists(audio_info['path']):
            os.remove(audio_info['path'])
        
        return jsonify({
            'success': True,
            'title': audio_info['title'],
            'duration': audio_info['duration'],
            'transcript': transcript,
            'insights': insights
        })
        
    except Exception as e:
        print(f"Fehler: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe-only', methods=['POST'])
def transcribe_only():
    """Nur Transkription ohne Analyse"""
    try:
        data = request.json
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({'error': 'Keine URL angegeben'}), 400
        
        audio_info = download_audio(youtube_url)
        transcript = transcribe_audio(audio_info['path'])
        
        if os.path.exists(audio_info['path']):
            os.remove(audio_info['path'])
        
        return jsonify({
            'success': True,
            'title': audio_info['title'],
            'duration': audio_info['duration'],
            'transcript': transcript
        })
        
    except Exception as e:
        print(f"Fehler: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_transcript():
    """Analysiert ein vorhandenes Transkript"""
    try:
        data = request.json
        transcript = data.get('transcript')
        use_claude = data.get('use_claude', True)
        
        if not transcript:
            return jsonify({'error': 'Kein Transkript angegeben'}), 400
        
        insights = extract_insights(transcript, use_claude)
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        print(f"Fehler: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
