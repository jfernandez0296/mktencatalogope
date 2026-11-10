#!/usr/bin/env bash
# One ElevenLabs TTS take per segment (premade voice Sarah speaking Spanish via eleven_multilingual_v2), trimmed and loudness-matched.
# The API key is injected by the credential proxy. Usage: ./generar-segmentos-elevenlabs.sh [voice_id] [ids]
set -euo pipefail
cd "$(dirname "$0")"
VOICE="${1:-EXAVITQu4vr4xnSDxMaL}"; SOLO="${2:-}"; MODEL="${MODEL:-eleven_multilingual_v2}"
mkdir -p seg
n=$(jq length segmentos.json)
for i in $(seq 0 $((n-1))); do
  id=$(jq -r ".[$i].id" segmentos.json); text=$(jq -r ".[$i].text" segmentos.json)
  if [ -n "$SOLO" ] && [[ ",$SOLO," != *",$id,"* ]]; then continue; fi
  body=$(jq -n --arg t "$text" --arg m "$MODEL" '{text:$t, model_id:$m, voice_settings:{stability:0.5, similarity_boost:0.75, style:0.25, use_speaker_boost:true}}')
  code=$(curl -sS -m 120 -o "seg/$id.mp3" -w "%{http_code}" -H "xi-api-key: dummy" -H "Content-Type: application/json" \
    "https://api.elevenlabs.io/v1/text-to-speech/$VOICE?output_format=mp3_44100_128" -d "$body")
  [ "$code" = 200 ] || { echo "$id: HTTP $code $(head -c 300 seg/$id.mp3)"; exit 1; }
  ffmpeg -y -loglevel error -i "seg/$id.mp3" -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,loudnorm=I=-19:TP=-2:LRA=7" -ar 44100 -ac 1 "seg/$id.wav"
  rm -f "seg/$id.mp3"
  echo "$id $(ffprobe -v error -show_entries format=duration -of csv=p=0 seg/$id.wav)"
done
