# Lowers the music under each voice segment (smooth 0.2 s ramps). Usage: ducking.py in.wav out.wav segmentos.json segdir
import json, subprocess, sys, os
inp, out, segf, segdir = sys.argv[1:5]
segs = json.load(open(segf)); ws = []
for x in segs:
    d = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',os.path.join(segdir,x['id']+'.wav')]).decode())
    s, e = x['start'], x['start'] + d
    ws.append('clip(min((t-%.3f+0.2)/0.2,(%.3f+0.2-t)/0.2),0,1)' % (s, e))
m = ws[0]
for w in ws[1:]: m = 'max(%s,%s)' % (m, w)
open(out + '.flt', 'w').write("volume='1-0.55*%s':eval=frame" % m)
subprocess.check_call(['ffmpeg','-y','-loglevel','error','-i',inp,'-filter_script:a',out + '.flt',out])
os.remove(out + '.flt')
