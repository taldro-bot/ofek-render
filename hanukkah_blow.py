"""28.11 Tal: "BLOW MIND" Hanukkah spot – 3 shots from Tal's prompts (A crane-up FPV, B ignition macro, C aerial reveal),
speed-ramp (fast A→B, dramatic slow-mo at ignition), zoom-punch transition, sparks, camera shake,
sound design only (wind at height, hydraulic hum, whoosh, sub-bass boom at ignition, fire crackle) – no music.
python hanukkah_blow.py LANG out.mp4"""
import sys, os, math, random, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import hanukkah_pro as P

ROOT = P.ROOT
DIR = os.path.join(ROOT, 'media', 'hanukkah', 'blow')
W, H, FPS, DUR = 1080, 1920, 30, 14.0
T_IGN = 4.3     # ignition moment


def crop(img, z, cx, cy):
    iw, ih = img.size; cw, ch = iw / z, ih / z
    x0 = min(max(0, cx * iw - cw / 2), iw - cw); y0 = min(max(0, cy * ih - ch / 2), ih - ch)
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BICUBIC)


def ramp_fast(p): return p ** 2.6          # accelerating
def ramp_out(p): return 1 - (1 - p) ** 3   # decelerating


rnd = random.Random(5)
SPARKS = [(rnd.uniform(.35, .75), rnd.uniform(.15, .45), rnd.uniform(-.25, .25), rnd.uniform(-.5, -.05), rnd.uniform(2, 6)) for _ in range(160)]


def sparks(img, t):
    if t < T_IGN: return img
    d = ImageDraw.Draw(img); k = t - T_IGN
    for (x, y, vx, vy, s) in SPARKS:
        px = (x + vx * k * .35) * W; py = (y + (vy * k + .25 * k * k) * .35) * H
        a = max(0, 255 - int(k * 55))
        if a and 0 < px < W and 0 < py < H:
            d.ellipse([px - s, py - s, px + s, py + s], fill=(255, 200 + int(s * 8), 90, a))
    return img


def frame(I, t, lang):
    if t < 3.2:                                   # A: FPV crane-up, accelerating
        p = ramp_fast(t / 3.2)
        fr = crop(I['A'], 1.35 - .15 * p, .5, .78 - .5 * p)
        if p > .35:                               # vertical motion blur when fast
            fr = Image.blend(fr, fr.filter(ImageFilter.BoxBlur(int(4 + 14 * p))), min(.7, p))
    elif t < 3.6:                                 # zoom-punch transition A→B
        q = (t - 3.2) / .4
        a = crop(I['A'], 1.2 + 1.2 * q, .5, .28)
        b = crop(I['B'], 1.6 - .45 * q, .55, .35)
        fr = Image.blend(a, b, q).filter(ImageFilter.GaussianBlur(6 * (1 - abs(q - .5) * 2)))
        fr = ImageEnhance.Brightness(fr).enhance(1 + .8 * (1 - abs(q - .5) * 2))
    elif t < 9.0:                                 # B: slow-mo push-in, ignition boom
        p = (t - 3.6) / 5.4
        z = 1.15 + .12 * p
        sh = .006 * math.exp(-(t - T_IGN) * 3) * math.sin(t * 90) if t > T_IGN else 0
        fr = crop(I['B'], z, .55 + sh, .35 + sh)
        boom = math.exp(-(t - T_IGN) * 4) if t > T_IGN else 0
        fr = ImageEnhance.Brightness(fr).enhance(1 + .55 * boom + .03 * math.sin(t * 21))
        if t > 8.4:
            fr = Image.blend(fr, crop(I['C'], 1.45, .48, .42), (t - 8.4) / .6)
    else:                                         # C: aerial pull-back reveal
        p = ramp_out((t - 9.0) / 5.0)
        fr = crop(I['C'], 1.45 - .45 * p, .48, .42 + .05 * p)
        fr = ImageEnhance.Brightness(fr).enhance(1 + .04 * math.sin(t * 6))
    img = sparks(fr.convert('RGBA'), t) if 3.6 <= t < 9.0 else fr.convert('RGBA')
    if t < .6: img.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - t / .6)))))
    rtl = lang == 'he'; d = ImageDraw.Draw(img)
    if t > 11.2:
        a = int(255 * P.ease((t - 11.2) / .8))
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        for y in range(1150, H): sd.line([(0, y), (W, y)], fill=(0, 0, 0, int(min(210, (y - 1150) * .5) * a / 255)))
        img.alpha_composite(sh); d = ImageDraw.Draw(img)
        e = P.END[lang]
        P.txt(d, (W / 2, 1420), e[0], 110, P.YEL, rtl, a)
        P.txt(d, (W / 2, 1545), e[1], 58, P.WHITE, rtl, a)
        P.txt(d, (W / 2, 1625), e[2], 38, P.WHITE, rtl, a)
    d.text((W - 40, H - 40), 'הדמיה' if rtl else 'AI', font=P.font(rtl, 26), fill=(230, 230, 230, 170), anchor='rs',
           **(dict(direction='rtl', language='he') if rtl else {}))
    return img.convert('RGB')


def sound(path):
    sr = 44100; n = int(sr * DUR); t = np.arange(n) / sr; rng = np.random.default_rng(3)
    out = np.zeros(n)
    noise = rng.standard_normal(n)
    # wind: low-passed noise with gusts, strongest during the climb
    wind = np.convolve(noise, np.ones(60) / 60, mode='same')
    gust = .6 + .4 * np.sin(2 * np.pi * .35 * t) * np.sin(2 * np.pi * .13 * t + 1)
    env = np.clip(1.2 - np.abs(t - 2.0) / 6, .25, 1)
    out += 2.2 * wind * gust * env
    # hydraulic hum while boom rises (0–3.4 s) and lowers (9–13 s)
    hum = (np.sin(2 * np.pi * 58 * t) + .5 * np.sin(2 * np.pi * 116 * t) + .25 * np.sign(np.sin(2 * np.pi * 29 * t))) * (1 + .2 * np.sin(2 * np.pi * 3 * t))
    henv = np.clip((3.4 - t) / 3.4, 0, 1) * (t < 3.4) + .5 * ((t > 9) & (t < 13)) * np.sin(np.clip((t - 9) / 4, 0, 1) * np.pi)
    out += .18 * hum * henv
    # whoosh at the zoom-punch (3.1–3.7 s)
    m = (t > 3.0) & (t < 3.8); k = (t[m] - 3.0) / .8
    out[m] += 1.4 * np.convolve(noise[m], np.ones(8) / 8, mode='same') * np.sin(np.pi * k) ** 2
    # sub-bass boom at ignition
    m = t >= T_IGN; k = t[m] - T_IGN
    f = 55 * np.exp(-k * .8) + 28
    out[m] += 1.6 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-k * 1.6)
    out[m] += .9 * noise[m] * np.exp(-k * 25)             # initial crack
    # fire crackle after ignition
    for _ in range(260):
        s = rng.uniform(T_IGN, DUR - .3); i = int(s * sr); L = int(sr * .012)
        if i + L < n: out[i:i + L] += rng.uniform(.1, .45) * rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4))
    out[-sr:] *= np.linspace(1, 0, sr)
    out = out / np.max(np.abs(out)) * .9
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out * 32767).astype(np.int16).tobytes())


def main():
    lang, out = sys.argv[1], sys.argv[2]
    I = {k: Image.open(os.path.join(DIR, k + '.jpg')).convert('RGB') for k in 'ABC'}
    tmp = tempfile.mkdtemp()
    for i in range(int(DUR * FPS)):
        frame(I, i / FPS, lang).save(os.path.join(tmp, '%04d.jpg' % i), quality=90)
    snd = os.path.join(tmp, 's.wav'); sound(snd)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, '%04d.jpg'), '-i', snd,
                    '-map', '0:v', '-map', '1:a', '-t', str(DUR), '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', out], check=True)
    print(out)


if __name__ == '__main__':
    main()
