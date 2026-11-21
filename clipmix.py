"""21.11 clip-mix machine: every run builds NEW videos from random 4s clips of Tal's real field videos
(clip library = branches clips-N listed in state/clips.txt), each with a different text (tips/questions/quiz/viral),
different procedurally-generated music (tempo/key/style), logo badge + Tal mascot + brand bar, and the end card.
usage: python clipmix.py COUNT  -> out/<id>.mp4 + out/<id>.json, prints ids"""
import os, sys, json, random, subprocess, datetime, urllib.request, wave, struct, math
import render as R
from kinds import QUESTION, QUIZ, TIP, REGS
from remix import VIRAL, CITIES

W, H, FPS, SEG = 1080, 1920, 30, 3.6
R.W, R.H, R.FPS = W, H, FPS
RAW = 'https://raw.githubusercontent.com/taldro-bot/ofek-render/'
OUT = os.path.abspath('out'); TMP = '/tmp/cm'
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)


def run(c):
    subprocess.run(c, check=True)


def get(url, dst):
    urllib.request.urlretrieve(url, dst); return dst


def music(path, secs, rnd):
    """original procedural track: kick/hat/bass/arp; random tempo, key, scale, pattern -> never the same twice"""
    sr = 44100; bpm = rnd.choice([92, 100, 108, 116, 124, 128]); beat = 60.0 / bpm
    root = 110.0 * 2 ** (rnd.randrange(12) / 12.0)
    scale = rnd.choice([[0, 3, 5, 7, 10], [0, 2, 4, 7, 9], [0, 2, 3, 7, 8], [0, 4, 5, 7, 11]])
    prog = [rnd.choice([0, 0, 3, 4, 5, 7]) for _ in range(4)]
    arp = [rnd.choice(scale) + 12 * rnd.choice([1, 1, 2]) for _ in range(8)]
    n = int(secs * sr); buf = [0.0] * n
    def add(t0, dur, f, amp, kind):
        i0 = int(t0 * sr); m = min(int(dur * sr), n - i0)
        for i in range(max(0, m)):
            t = i / sr; env = math.exp(-t * (6 if kind != 'kick' else 18))
            if kind == 'kick': v = math.sin(2 * math.pi * (50 + 90 * math.exp(-t * 30)) * t) * env
            elif kind == 'hat': v = (rnd.random() * 2 - 1) * math.exp(-t * 60)
            elif kind == 'bass': v = (1 if math.sin(2 * math.pi * f * t) > 0 else -1) * 0.5 * math.exp(-t * 3)
            else: v = math.sin(2 * math.pi * f * t) * env + 0.3 * math.sin(4 * math.pi * f * t) * env
            buf[i0 + i] += v * amp
    t = 0.0; k = 0
    while t < secs:
        bar = (k // 4) % 4; deg = prog[bar]
        if k % 4 in (0, 2) or rnd.random() < 0.15: add(t, 0.35, 0, 0.9, 'kick')
        add(t + beat / 2, 0.05, 0, 0.18, 'hat')
        add(t, beat * 0.9, root * 2 ** (deg / 12) / 2, 0.22, 'bass')
        for j in range(2):
            add(t + j * beat / 2, beat / 2, root * 2 ** ((deg + arp[(k * 2 + j) % 8]) / 12), 0.16, 'arp')
        t += beat; k += 1
    pk = max(1e-6, max(abs(x) for x in buf))
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b''.join(struct.pack('<h', int(32000 * 0.85 * x / pk)) for x in buf))


def ass(path, title, lines, total):
    RLM = '‏'; per = (total - 0.5) / len(lines)
    ev = ''.join(f"Dialogue: 1,0:00:{0.5 + i * per:05.2f},0:00:{min(total, 0.5 + (i + 1) * per):05.2f},L,,0,0,0,,{{\\fad(150,100)}}{RLM}{l}{RLM}\n"
                 for i, l in enumerate(lines))
    open(path, 'w', encoding='utf-8').write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: T,Heebo,80,&H00FFFFFF,&H00FFFFFF,&H00B05A12,&H00000000,1,0,0,0,100,100,0,0,3,24,0,8,50,50,140,-1
Style: L,Heebo,74,&H0000F0FF,&H00FFFFFF,&H00000000,&H78000000,1,0,0,0,100,100,0,0,1,7,3,5,70,70,0,-1
Style: F,Heebo,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,3,16,0,2,40,40,110,-1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:01:00.00,T,,0,0,0,,{{\\fad(300,0)}}{RLM}{title}{RLM}
Dialogue: 0,0:00:00.00,0:01:00.00,F,,0,0,0,,{RLM}אופק את טל מנופים · 050-9081114 · tal83.com{RLM}
""" + ev)


def main():
    cnt = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    sp = 'state/clipmix.json'; st = json.load(open(sp)) if os.path.exists(sp) else {'n': 0}
    branches = [b for b in open('state/clips.txt').read().split() if b] if os.path.exists('state/clips.txt') else []
    lib = []
    for b in branches:
        try: lib += [(b, x) for x in urllib.request.urlopen(RAW + b + '/list.txt', timeout=30).read().decode().split()]
        except Exception as e: print('skip', b, e, file=sys.stderr)
    if len(lib) < 8: print('library too small', len(lib), file=sys.stderr); return
    texts = [('tip', t) for t in TIP] + [('question', t) for t in QUESTION] + [('quiz', t) for t in QUIZ] + [('viral', t) for t in VIRAL] + [('regs', t) for t in REGS]
    day = datetime.date.today().strftime('%y%m%d'); ids = []
    for _ in range(cnt):
        n = st['n']; rnd = random.Random(n * 104729 + 3); jid = 'r%s%03d' % (day, 700 + n % 100)
        kind, (title, lines) = texts[n % len(texts)]; city = rnd.choice(CITIES)
        title = title.format(c=city); lines = [l.format(c=city) for l in lines]
        picks = rnd.sample(lib, min(len(lib), len(lines) + 2))
        segs = []
        for i, (b, x) in enumerate(picks):
            src = get(RAW + b + '/clips/' + x, f'{TMP}/s{i}.mp4'); dst = f'{TMP}/v{i}.mp4'
            sp_ = rnd.choice([1.0, 1.0, 1.25, 0.8, 2.0])
            fx = ''.join([',reverse' if rnd.random() < 0.25 else '', ',hflip' if rnd.random() < 0.3 else '',
                          rnd.choice(['', '', ',eq=saturation=1.35:contrast=1.08', ',eq=gamma=0.9:saturation=0.8', ',colorbalance=rs=0.08:bs=-0.06', ',hue=s=0'])])
            vf = (f"setpts=PTS/{sp_},fps={FPS}{fx},split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=26:2,eq=brightness=-0.12[bg];"
                  f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease,eq=contrast=1.07:saturation=1.18[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,"
                  f"zoompan=z='min(zoom+0.0009,1.08)':d=1:s={W}x{H}:fps={FPS}")
            run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-stream_loop', '2', '-i', src, '-t', str(SEG), '-filter_complex', '[0:v]' + vf,
                 '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', dst]); segs.append(dst)
        lst = f'{TMP}/l.txt'; open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
        body = f'{TMP}/body.mp4'; total = SEG * len(segs); a = f'{TMP}/t.ass'; ass(a, title, lines, total)
        run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', R.BADGE, '-i', R.MASCOT,
             '-filter_complex', f"[1:v]scale=180:-2[lg];[2:v]scale=-2:430[ms];[0:v][lg]overlay=W-w-34:34[a];[a][ms]overlay=10:H-h-200,ass={a}:fontsdir={R.FONT_DIR},format=yuv420p[v]",
             '-map', '[v]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', body])
        end = f'{TMP}/end.mp4'
        if not os.path.exists(end): R.end_card(end, 4.0)
        T = total + 4.0; mus = f'{TMP}/m.wav'; music(mus, T + 1, rnd)
        out = os.path.join(OUT, jid + '.mp4')
        run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', body, '-i', end, '-i', mus, '-filter_complex',
             f"[0:v][1:v]xfade=transition=fade:duration=0.4:offset={total - 0.4:.2f}[v];[2:a]atrim=0:{T - 0.4:.2f},afade=t=in:d=0.4,afade=t=out:st={T - 2.2:.2f}:d=2,volume=0.7[a]",
             '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-maxrate', '6M', '-bufsize', '12M',
             '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out])
        json.dump({'id': jid, 'title': title, 'lines': lines, 'lang': 'he', 'kind': 'clipmix-' + kind,
                   'clips': [b + '/' + x for b, x in picks]}, open(os.path.join(OUT, jid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        st['n'] = n + 1; ids.append(jid)
    json.dump(st, open(sp, 'w')); print(' '.join(ids))


if __name__ == '__main__':
    main()
