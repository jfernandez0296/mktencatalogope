#!/usr/bin/env bash
# One Gemini TTS take per segment (voice Leda), trimmed and loudness-matched. The API key is added by the credential proxy.
# Usage: ./generar-segmentos-gemini.sh [voz] [ids] [modelo]
set -euo pipefail
cd "$(dirname "$0")"
VOICE="${1:-Leda}"; SOLO="${2:-}"; MODEL="${3:-gemini-3.8-flash-tts}"
STYLE="${STYLE-}"
mkdir -p seg
n=$(jq length segmentos.json)
for i in $(seq 0 $((n-1))); do
  id=$(jq -r ".[$i].id" segmentos.json); text=$(jq -r ".[$i].text" segmentos.json)
  if [ -n "$SOLO" ] && [[ ",$SOLO," != *",$id,"* ]]; then continue; fi
  body=$(jq -n --arg t "$STYLE$text" --arg v "$VOICE" '{contents:[{parts:[{text:$t}]}],generationConfig:{responseModalities:["AUDIO"],speechConfig:{voiceConfig:{prebuiltVoiceConfig:{voiceName:$v}}}}}')
  data=""; mime=""
  for try in 1 2 3 4 5; do
    resp=$(curl -sS -m 120 -H "Content-Type: application/json" "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent" -d "$body")
    data=$(echo "$resp" | jq -r '.candidates[0].content.parts[0].inlineData.data // empty')
    mime=$(echo "$resp" | jq -r '.candidates[0].content.parts[0].inlineData.mimeType // empty')
    [ -n "$data" ] && break
    echo "$id: sin audio ($(echo "$resp" | jq -r '.error.message // .candidates[0].finishReason // "?"' | head -c 90)); espero 30 s"; sleep 30
  done
  [ -z "$data" ] && { echo "$id: FALLÓ"; exit 1; }
  if [[ "$mime" == audio/wav* ]]; then echo "$data" | base64 -d > "seg/$id.raw.wav"
  else echo "$data" | base64 -d > "seg/$id.pcm"; ffmpeg -y -loglevel error -f s16le -ar 24000 -ac 1 -i "seg/$id.pcm" "seg/$id.raw.wav"; rm -f "seg/$id.pcm"; fi
  ffmpeg -y -loglevel error -i "seg/$id.raw.wav" -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,loudnorm=I=-19:TP=-2:LRA=7" -ar 44100 -ac 1 "seg/$id.wav"
  rm -f "seg/$id.raw.wav" "seg/$id.trim.wav"
  echo "$id $(ffprobe -v error -show_entries format=duration -of csv=p=0 seg/$id.wav)"
done
