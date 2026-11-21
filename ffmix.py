"""16.11: fast-forward (timelapse) mixes from long field videos.
usage: python ffmix.py SRC_DIR OUT_DIR
For every video in SRC_DIR -> ffNNN.mp4 (9:16, ~40s timelapse + end card), plus ff-mix.mp4 (best 8s of each)."""
import os, sys, json, subprocess
import render as R

SRC, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
R.W, R.H, R.FPS = W, H, FPS
MUSIC = os.path.join(R.ROOT, 'assets', 'music', 'upbeat1.wav')
BODY = 40.0


def run(c):
    print(' '.join(c[:6]), flush=True); subprocess.run(c, check=True)


def probe(p):
    o = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_type',
                                            '-of', 'json', p]))
    v = [s for s in o['streams'] if s.get('codec_type') == 'video'][0]
    return float(o['format']['duration']), v['width'], v['height']


def ass(path, title, sub, hook=''):
    RLM = '‏'
    open(path, 'w', encoding='utf-8').write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: T,Heebo,92,&H00FFFFFF,&H00FFFFFF,&H00B05A12,&H00000000,1,0,0,0,100,100,0,0,3,26,0,8,40,40,150,-1
Style: K,Heebo,62,&H0000F0FF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,4,2,8,40,40,320,-1
Style: H,Heebo,112,&H0000F0FF,&H00FFFFFF,&H00000000,&HA0000000,1,0,0,0,100,100,0,0,1,12,6,5,60,60,0,-1
Style: F,Heebo,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,3,18,0,2,40,40,120,-1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:01:00.00,T,,0,0,0,,{{\\fad(300,0)}}{RLM}{title}{RLM}
Dialogue: 0,0:00:00.30,0:01:00.00,K,,0,0,0,,{{\\fad(400,0)}}{RLM}{sub}{RLM}
Dialogue: 0,0:00:00.00,0:01:00.00,F,,0,0,0,,{RLM}אופק את טל מנופים · 050-9081114{RLM}
""" + (f"Dialogue: 2,0:00:00.00,0:00:01.80,H,,0,0,0,,{{\\pos(540,880)\\fscx40\\fscy40\\t(0,160,\\fscx118\\fscy118)\\t(160,260,\\fscx100\\fscy100)\\fad(0,200)}}{RLM}{hook}{RLM}\n" if hook else ''))


def timelapse(src, out, secs=BODY, start=0.0, span=None, title='⏩ הילוך מהיר', sub='עבודה אמיתית בשטח', hook=''):
    d, w, h = probe(src)
    span = span or (d - start)
    k = max(span / secs, 1.0)
    pre = ['-skip_frame', 'nokey'] if k >= 25 else []
    a = os.path.join(OUT, 'tmp.ass'); ass(a, title, sub, hook)
    if w >= h:
        vf = (f"setpts=PTS/{k:.4f},fps={FPS},split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:2,eq=brightness=-0.12[bg];"
              f"[b]scale={W}:-2,eq=contrast=1.06:saturation=1.15[fg];[bg][fg]overlay=0:(H-h)/2")
    else:
        vf = f"setpts=PTS/{k:.4f},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},eq=contrast=1.06:saturation=1.15"
    vf += f"[v0];[1:v]scale=190:-2[lg];[v0][lg]overlay=W-w-36:36,ass={a}:fontsdir={R.FONT_DIR},format=yuv420p[v]"
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y'] + pre + ['-ss', str(start), '-t', str(span), '-i', src, '-i', R.BADGE,
         '-filter_complex', '[0:v]' + vf, '-map', '[v]', '-an', '-t', f'{secs:.2f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', out])


def finish(body, out):
    end = os.path.join(OUT, 'end.mp4')
    if not os.path.exists(end):
        R.end_card(end, 4.0)
    b = probe(body)[0]
    T = b + 4.0
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', body, '-i', end, '-stream_loop', '-1', '-i', MUSIC, '-filter_complex',
         f"[0:v][1:v]xfade=transition=fade:duration=0.4:offset={b - 0.4:.2f}[v];[2:a]atrim=0:{T - 0.4:.2f},afade=t=in:d=0.5,afade=t=out:st={T - 2.4:.2f}:d=2,volume=0.8[a]",
         '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-maxrate', '6M', '-bufsize', '12M',
         '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out])


TOPIC = os.environ.get('FF_TITLE', 'עבודת מנוף סל מהשטח')


def reverse(src, out):  # 4s chunks – whole-clip reverse gets OOM-killed
    d = probe(src)[0]; parts = []; t = 0.0; k = 0
    while t < d - 0.05:
        c = os.path.join(OUT, 'rv%02d.mp4' % k)
        run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-t', '4', '-i', src, '-vf', 'reverse', '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', c])
        parts.append(c); t += 4; k += 1
    lst = os.path.join(OUT, 'rv.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in reversed(parts)))
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out])


vids = sorted(f for f in os.listdir(SRC) if f.lower().endswith(('.mp4', '.mov')))
start_n = int(os.environ.get('FF_START', '1'))
bits = []
for i, f in enumerate(vids):
    code = 'ff%03d' % (start_n + i)
    src = os.path.join(SRC, f)
    body = os.path.join(OUT, code + '-body.mp4')
    timelapse(src, body)
    finish(body, os.path.join(OUT, code + '.mp4'))
    d = probe(src)[0]
    HK = R.HOOKS['he']
    # 20.11 (Tal: "להשתגע איתו"): reverse version + 4 part-shorts per source
    rb = os.path.join(OUT, 'rbody.mp4')
    timelapse(src, rb, title='⏪ אחורה בזמן', sub=TOPIC)
    reverse(rb, os.path.join(OUT, 'rrev.mp4'))
    finish(os.path.join(OUT, 'rrev.mp4'), os.path.join(OUT, 'ffr%03d.mp4' % (start_n + i)))
    for q in range(4):
        sb = os.path.join(OUT, 'sbody.mp4')
        timelapse(src, sb, secs=22.0, start=d * q / 4, span=d / 4, title=TOPIC, sub='חלק %d מתוך 4' % (q + 1), hook=HK[(i + q + 2) % len(HK)])
        finish(sb, os.path.join(OUT, 'ffs%03d%s.mp4' % (start_n + i, 'abcd'[q])))
    bit = os.path.join(OUT, f'bit{i}.mp4')   # mix: middle third of the job at high speed, 8s
    timelapse(src, bit, secs=8.0, start=d * 0.3, span=d * 0.4, title='⏩ עבודות מנוף בהילוך מהיר', sub='אופק את טל מנופים')
    bits.append(bit)
    print('DONE', code, f, round(d), flush=True)

if len(bits) > 1:
    lst = os.path.join(OUT, 'bits.txt'); open(lst, 'w').write(''.join(f"file '{b}'\n" for b in bits))
    mixb = os.path.join(OUT, 'mix-body.mp4')
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', mixb])
    finish(mixb, os.path.join(OUT, 'ff-mix-%03d.mp4' % start_n))
