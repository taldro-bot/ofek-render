"""27.11 Tal: Hanukkah animation – basket crane lifts Tal (harness) to a giant hanukkiah and lights night N.
python hanukkah.py N [out.mp4]   (N = 1..8). Pure PIL + ffmpeg, 9:16, ~10 s, original drawing (no brands)."""
import sys, os, math, random, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1080, 1920, 30, 12.0
FONT = os.path.join(ROOT, 'assets', 'fonts', 'Heebo.ttf')
NIGHT = ['נר ראשון', 'נר שני', 'נר שלישי', 'נר רביעי', 'נר חמישי', 'נר שישי', 'נר שביעי', 'נר שמיני']
SAFE = ['גם בהדלקה – רתמה!', 'בגובה? קודם קסדה.', 'סל מוסמך = הדלקה בטוחה', 'מפעיל מוסמך, תמיד.',
        'בודקים את הרתמה לפני שעולים', 'רוח חזקה? לא עולים.', 'שטח מגודר מתחת לסל', 'אור גדול – ובטיחות גדולה']
YEL, GOLD, WHITE, DARK = (255, 206, 60), (232, 182, 60), (255, 255, 255), (14, 18, 40)


def f(sz): return ImageFont.truetype(FONT, sz)


def text(d, xy, s, sz, fill=WHITE, anchor='mm', stroke=0):
    d.text(xy, s, font=f(sz), fill=fill, anchor=anchor, direction='rtl', language='he',
           stroke_width=stroke, stroke_fill=(0, 0, 0))


def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def background():
    bg = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(10 + 25 * k), int(14 + 30 * k), int(45 + 50 * k)))
    rnd = random.Random(7)
    for _ in range(140):
        x, y, r = rnd.randrange(W), rnd.randrange(int(H * .55)), rnd.choice([1, 1, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 230))
    # Jerusalem-stone style skyline
    x = 0
    while x < W:
        bw, bh = rnd.randrange(90, 190), rnd.randrange(180, 420)
        d.rectangle([x, H - 330 - bh, x + bw, H], fill=(46, 44, 60))
        for wy in range(H - 310 - bh, H - 340, 60):
            for wx in range(x + 18, x + bw - 25, 42):
                if rnd.random() < .45: d.rectangle([wx, wy, wx + 18, wy + 26], fill=(255, 214, 120))
        x += bw + rnd.randrange(4, 20)
    d.rectangle([0, H - 330, W, H], fill=(38, 38, 44))           # street
    for x in range(0, W, 120): d.rectangle([x, H - 200, x + 60, H - 190], fill=(200, 200, 200))
    return bg


# hanukkiah geometry
HX, HBASE, HTOP = 640, H - 330, 760          # centre x, base y, candle-holder y
ARM = [HX + (i - 4) * 62 for i in range(9)]  # 9 cups, index 4 = shamash


def hanukkiah(d):
    d.rectangle([HX - 22, HTOP + 40, HX + 22, HBASE], fill=GOLD)
    d.polygon([(HX - 140, HBASE), (HX + 140, HBASE), (HX + 60, HBASE - 70), (HX - 60, HBASE - 70)], fill=GOLD)
    for i, x in enumerate(ARM):
        if i == 4: continue
        r = abs(x - HX)
        d.arc([HX - r, HTOP + 40 - r, HX + r, HTOP + 40 + r], 0, 180, fill=GOLD, width=14)
    for i, x in enumerate(ARM):
        y = HTOP - (60 if i == 4 else 0)
        d.rectangle([x - 22, y, x + 22, y + 26], fill=GOLD)
        d.rectangle([x - 9, y - 70, x + 9, y], fill=(250, 245, 235))


def flame(img, x, y, t, k):
    fl = Image.new('RGBA', (120, 180), (0, 0, 0, 0))
    g = ImageDraw.Draw(fl)
    s = 1 + .12 * math.sin(t * 14 + k)
    g.ellipse([60 - 40 * s, 40, 60 + 40 * s, 170], fill=(255, 170, 40, 90))
    g.ellipse([60 - 18 * s, 70 - 20 * s, 60 + 18 * s, 160], fill=(255, 200, 60, 255))
    g.ellipse([60 - 8, 115, 60 + 8, 158], fill=(255, 255, 220, 255))
    fl = fl.filter(ImageFilter.GaussianBlur(2))
    img.alpha_composite(fl, (int(x - 60), int(y - 170)))


def crane(img, d, lift):
    # white truck, bottom-left
    tx, ty = 40, H - 420
    d.rectangle([tx, ty + 40, tx + 330, ty + 170], fill=(240, 240, 240))
    d.rectangle([tx + 330, ty + 70, tx + 430, ty + 170], fill=(225, 225, 225))
    d.rectangle([tx + 345, ty + 85, tx + 415, ty + 125], fill=(120, 170, 220))
    for wx in (tx + 70, tx + 250, tx + 380):
        d.ellipse([wx - 38, ty + 140, wx + 38, ty + 216], fill=(20, 20, 20)); d.ellipse([wx - 16, ty + 162, wx + 16, ty + 194], fill=(150, 150, 150))
    for ox in (tx - 10, tx + 300):                                 # outriggers + pads
        d.rectangle([ox, ty + 150, ox + 16, ty + 240], fill=(255, 190, 0)); d.rectangle([ox - 20, ty + 238, ox + 36, ty + 250], fill=(60, 60, 60))
    for cx in (tx - 60, tx + 470):                                 # orange cones
        d.polygon([(cx, H - 160), (cx + 40, H - 160), (cx + 20, H - 230)], fill=(255, 120, 0)); d.rectangle([cx + 8, H - 205, cx + 32, H - 192], fill=WHITE)
    # boom from turret to basket
    px, py = tx + 120, ty + 40
    bx = 210 + (ARM[1] - 150 - 210) * lift
    by = H - 520 + (HTOP - 190 - (H - 520)) * lift
    d.line([(px, py), ((px + bx) / 2, by + 120)], fill=(20, 20, 20), width=34)
    d.line([((px + bx) / 2, by + 120), (bx, by + 40)], fill=(255, 200, 0), width=26)
    d.ellipse([px - 30, py - 30, px + 30, py + 30], fill=(30, 30, 30))
    # basket + Tal
    av = Image.open(os.path.join(ROOT, 'assets', 'mascot_round.png')).convert('RGBA').resize((190, 190))
    img.alpha_composite(av, (int(bx - 95), int(by - 175)))
    d = ImageDraw.Draw(img)
    d.rectangle([bx - 110, by - 10, bx + 110, by + 70], fill=(255, 200, 0), outline=(30, 30, 30), width=6)
    for k in range(-80, 100, 40): d.line([(bx + k, by - 10), (bx + k, by + 70)], fill=(30, 30, 30), width=4)
    d.line([(bx - 60, by - 8), (bx - 60, by - 40), (bx - 20, by - 40)], fill=(255, 90, 0), width=9)  # harness lanyard clipped to basket
    return bx, by, d


def frame(bg, n, t):
    img = bg.copy().convert('RGBA'); d = ImageDraw.Draw(img)
    hanukkiah(d)
    lift = ease(t / 3.0)
    bx, by, d = crane(img, d, lift)
    # lighting: shamash first, then candles right→left in order (night n = n candles)
    order = [4] + [8 - i for i in range(n)]
    lit_t = [3.2 + i * 0.55 for i in range(len(order))]
    for k, (i, lt) in enumerate(zip(order, lit_t)):
        if t >= lt:
            y = HTOP - (60 if i == 4 else 0) - 70
            flame(img, ARM[i], y, t, k)
    d = ImageDraw.Draw(img)
    # texts
    a = ease((t - .3) / .6)
    if a > 0: text(d, (W / 2, 210), NIGHT[n - 1] + ' של חנוכה', 92, YEL, stroke=4)
    if t > 3.0: text(d, (W / 2, 330), SAFE[n - 1], 62, WHITE, stroke=3)
    if 3.2 <= t < lit_t[-1] + .9:
        text(d, (W / 2, 1120), "בָּרוּךְ אַתָּה ה' אֱלֹקֵינוּ מֶלֶךְ הָעוֹלָם", 50, WHITE, stroke=3)
        text(d, (W / 2, 1195), 'אֲשֶׁר קִדְּשָׁנוּ בְּמִצְוֹתָיו וְצִוָּנוּ', 50, WHITE, stroke=3)
        text(d, (W / 2, 1270), 'לְהַדְלִיק נֵר חֲנֻכָּה', 62, YEL, stroke=3)
    if t >= lit_t[-1] + .9:
        text(d, (W / 2, 1150), 'חנוכה שמח!', 120, YEL, stroke=5)
        text(d, (W / 2, 1270), 'מנוף סל להדלקות חנוכייה ענקית', 54, WHITE, stroke=3)
    # brand bar
    d.rectangle([0, H - 120, W, H], fill=(10, 10, 10)); d.rectangle([0, H - 126, W, H - 120], fill=YEL)
    text(d, (W / 2, H - 60), 'אופק את טל מנופים · tal83.com · 050-9081114', 46, WHITE)
    return img.convert('RGB')


def melody(path, seed=5783):
    """Original festive bell tune (pentatonic, generated) + soft pad. No borrowed melody."""
    import numpy as np, wave
    sr, bpm = 44100, 112
    beat = 60 / bpm
    rnd = random.Random(seed)
    scale = [0, 2, 4, 7, 9, 12, 14, 16]
    notes, p = [], 4
    for bar in range(int(DUR / (4 * beat)) + 1):
        for b in range(4):
            p = max(0, min(len(scale) - 1, p + rnd.choice([-2, -1, 1, 1, 2])))
            notes.append((bar * 4 + b, scale[p], .5 if b % 2 else .7))
            if rnd.random() < .35: notes.append((bar * 4 + b + .5, scale[max(0, p - 1)], .35))
    n = int(sr * DUR); out = np.zeros(n)
    tt = np.arange(int(sr * 1.6)) / sr
    for st, semi, vol in notes:
        fq = 523.25 * 2 ** (semi / 12)
        tone = (np.sin(2 * np.pi * fq * tt) + .4 * np.sin(2 * np.pi * fq * 2.76 * tt) + .2 * np.sin(2 * np.pi * fq * 5.4 * tt)) * np.exp(-tt * 3.2)
        i = int(st * beat * sr)
        if i >= n: continue
        seg = tone[:n - i] * vol; out[i:i + len(seg)] += seg
    ta = np.arange(n) / sr
    for k, root in enumerate([261.63, 220.0, 174.61, 196.0] * 4):
        a, b = int(k * 4 * beat * sr), int((k + 1) * 4 * beat * sr)
        if a >= n: break
        seg = ta[a:min(b, n)]
        out[a:min(b, n)] += .12 * (np.sin(2 * np.pi * root * seg) + np.sin(2 * np.pi * root * 1.5 * seg))
    out = out / np.max(np.abs(out)) * .8
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    out = sys.argv[2] if len(sys.argv) > 2 else 'hanukkah-%d.mp4' % n
    bg = background()
    tmp = tempfile.mkdtemp()
    for i in range(int(DUR * FPS)):
        frame(bg, n, i / FPS).save(os.path.join(tmp, '%04d.jpg' % i), quality=90)
    music = os.path.join(tmp, 'bells.wav'); melody(music)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, '%04d.jpg'),
                    '-i', music, '-filter_complex', '[1:a]volume=0.9,afade=t=out:st=%s:d=1.5[a]' % (DUR - 1.5),
                    '-map', '0:v', '-map', '[a]', '-t', str(DUR), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
    print(out)


if __name__ == '__main__':
    main()
