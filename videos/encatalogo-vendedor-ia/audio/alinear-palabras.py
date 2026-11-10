# Word timestamps per segment via ElevenLabs forced alignment (key injected by the proxy). Adds "words": [[w, start, end]] to segmentos.json.
import json, subprocess, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
segs = json.load(open("segmentos.json"))
for s in segs:
    out = subprocess.check_output(["curl", "-sS", "-m", "120", "-H", "xi-api-key: proxy", "-F", f"file=@seg/{s['id']}.wav",
                                   "-F", f"text={s['text']}", "https://api.elevenlabs.io/v1/forced-alignment"])
    r = json.loads(out)
    s["words"] = [[w["text"], round(w["start"], 3), round(w["end"], 3)] for w in r["words"] if w["text"].strip()]
    assert len(s["words"]) == len(s["text"].split()), (s["id"], len(s["words"]))
    print(s["id"], len(s["words"]))
json.dump(segs, open("segmentos.json", "w"), ensure_ascii=False, indent=1)
