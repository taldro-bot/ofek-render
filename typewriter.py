"""21.11 typewriter machine: solid background, Tal's text typed letter by letter with typewriter clicks,
male Soniox voice (dub pipeline, job kind 'diary'), avatar + brand bar. 
  python typewriter.py new        -> creates the next diary job in jobs/ + state/pending.txt (prints id)
  python typewriter.py --job J    -> renders out/<id>.mp4 (needs audio_url filled by dubrender.py)"""
import os, sys, json, random, subprocess, datetime, urllib.request, wave, struct, math

from kinds import DIARY
W, H, FPS = 1080, 1920, 30
OUT = os.path.abspath('out'); TMP = '/tmp/tw'; os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
FONT = 'assets/fonts/Heebo.ttf'
BG = [(20, 22, 26), (250, 246, 236), (14, 30, 52), (36, 24, 18)]


def run(c): subprocess.run(c, check=True)


def new_job():
    sp = 'state/diary.json'; st = json.load(open(sp)) if os.path.exists(sp) else {'n': 0}
    n = st['n']; title, lines = DIARY[n % len(DIARY)]
    jid = 'r%s%03d' % (datetime.date.today().strftime('%y%m%d'), 600 + n % 100)
    json.dump({'id': jid, 'title': title, 'lines': lines, 'lang': 'he', 'kind': 'diary', 'typewriter': True},
              open('jobs/%s.json' % jid, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open('state/pending.txt', 'a').write(jid + '\n'); st['n'] = n + 1; json.dump(st, open(sp, 'w')); print(jid)


def clicks(path, times, dur):
    sr = 44100; buf = [0.0] * int(dur * sr); rnd = random.Random(1)
    for t, kind in times:
        i0 = int(t * sr); L = int(0.05 * sr) if kind == 'k' else int(0.6 * sr)
        for i in range(L):
            if i0 + i >= len(buf): break
            x = i / sr
            v = (rnd.random() * 2 - 1) * math.exp(-x * 90) * 0.55 + math.sin(2 * math.pi * 1800 * x) * math.exp(-x * 60) * 0.25 if kind == 'k' \
                else math.sin(2 * math.pi * 2600 * x) * math.exp(-x * 7) * 0.35        # 'b' = bell at line end
            buf[i0 + i] += v
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b''.join(struct.pack('<h', max(-32767, min(32767, int(28000 * x)))) for x in buf))


def render(j, voice):
    from PIL import Image, ImageDraw, ImageFont
    vdur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', voice]).decode().strip())
    T = vdur + 2.5; rnd = random.Random(hash(j['id']) & 0xffff); bg = rnd.choice(BG); dark = sum(bg) < 300
    fg = (245, 240, 228) if dark else (30, 30, 34); acc = (255, 194, 14)
    f_t = ImageFont.truetype(FONT, 64); f_l = ImageFont.truetype(FONT, 56)
    lines = j['lines']; total = sum(len(l) for l in lines); per = (vdur * 0.92) / max(1, total)
    # schedule: chars typed through the voice; bell after each line
    sched = []; t = 0.6; times = []
    for li, l in enumerate(lines):
        for ci in range(len(l)):
            sched.append((t, li, ci + 1)); times.append((t, 'k') if l[ci] != ' ' else (t, 's')); t += per
        times.append((t, 'b')); t += 0.15
    times = [x for x in times if x[1] != 's']
    av = Image.open('assets/mascot_tal.png').convert('RGBA'); cx, cy, r = 158, 235, 158
    head = av.crop((cx - r, cy - r, cx + r, cy + r)).resize((230, 230))
    mask = Image.new('L', (230, 230), 0); ImageDraw.Draw(mask).ellipse([0, 0, 229, 229], fill=255)
    base = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(base)
    d.ellipse([W // 2 - 125, 150, W // 2 + 125, 400], fill=acc); circ = Image.new('RGBA', (230, 230), (255, 206, 60, 255)); circ.alpha_composite(head)
    base.paste(circ, (W // 2 - 115, 160), mask)
    tw = d.textlength(j['title'], font=f_t); d.text(((W - tw) / 2, 440), j['title'], font=f_t, fill=acc if dark else (176, 112, 0))
    d.rectangle([0, H - 170, W, H], fill=(18, 18, 20)); d.rectangle([0, H - 176, W, H - 170], fill=acc)
    s = 'אופק את טל מנופים · 050-9081114 · tal83.com'; f_f = ImageFont.truetype(FONT, 42); sw = d.textlength(s, font=f_f)
    d.text(((W - sw) / 2, H - 122), s, font=f_f, fill=(255, 255, 255))
    frames = int(T * FPS); fdir = f'{TMP}/f'; os.makedirs(fdir, exist_ok=True)
    def wrap(txt):   # wrap one Hebrew line to the width
        out, cur = [], ''
        for w_ in txt.split(' '):
            c2 = (cur + ' ' + w_).strip()
            if d.textlength(c2, font=f_l) > W - 160 and cur: out.append(cur); cur = w_
            else: cur = c2
        return out + [cur]
    k = 0; state = (0, 0)
    for fi in range(frames):
        tt = fi / FPS
        while k < len(sched) and sched[k][0] <= tt: state = (sched[k][1], sched[k][2]); k += 1
        im = base.copy(); dr = ImageDraw.Draw(im); y = 600
        for li in range(state[0] + 1 if k else 0):
            txt = lines[li] if li < state[0] else lines[li][:state[1]]
            for wl in wrap(txt):
                lw = dr.textlength(wl, font=f_l); dr.text((W - 80 - lw, y), wl, font=f_l, fill=fg); y += 82
            y += 26
        if (fi // 15) % 2 == 0 and k < len(sched): dr.rectangle([W - 86 - (0 if not k else 0), y - 104, W - 80, y - 40], fill=acc)   # blinking cursor
        im.save(f'{fdir}/{fi:05d}.jpg', quality=90)
    ck = f'{TMP}/clicks.wav'; clicks(ck, times, T)
    out = os.path.join(OUT, j['id'] + '.mp4')
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{fdir}/%05d.jpg', '-i', voice, '-i', ck, '-filter_complex',
         '[1:a]adelay=500|500,volume=1.5[v];[2:a]volume=0.45[c];[v][c]amix=inputs=2:duration=longest:normalize=0[a]',
         '-map', '0:v', '-map', '[a]', '-t', f'{T:.2f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out])
    json.dump({'id': j['id'], 'title': j['title'] + ' | טל מאופק את טל מנופים', 'lines': j['lines'], 'lang': 'he', 'kind': 'diary'},
              open(os.path.join(OUT, j['id'] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    if sys.argv[1] == 'new': new_job()
    else:
        j = json.load(open(sys.argv[2])); v = f'{TMP}/voice.mp3'; urllib.request.urlretrieve(j['audio_url'], v); render(j, v)
