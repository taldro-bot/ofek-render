"""28.11 Tal: professional realistic Hanukkah film – Orthodox man in a basket crane lights a giant menorah in Jerusalem.
4 AI stills (media/hanukkah/pro/scene1-4.jpg) edited like a film: one camera move per shot (crane-up, push-in,
macro push-in, pull-back reveal), flame flicker, film grain, letterbox fade, NO music – narration only (oil-jar story).
python hanukkah_pro.py LANG out.mp4   (he/en/ru/fr; edge-tts voice, male, never Hila)"""
import sys, os, math, random, asyncio, subprocess, tempfile
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
PRO = os.path.join(ROOT, 'media', 'hanukkah', 'pro')
W, H, FPS = 1080, 1920, 30
SHOTS = [  # (start, end, image, move)
    (0.0, 4.6, 'scene1.jpg', 'craneup'),
    (4.0, 8.6, 'scene2.jpg', 'pushin'),
    (8.0, 12.1, 'scene3.jpg', 'macro'),
    (11.5, 17.0, 'scene4.jpg', 'pullback'),
]
DUR = 17.0
VOICE = {'he': 'he-IL-AvriNeural', 'en': 'en-US-GuyNeural', 'ru': 'ru-RU-DmitryNeural', 'fr': 'fr-FR-HenriNeural'}
NARR = {
 'he': 'לפני יותר מאלפיים שנה, נמצא בבית המקדש פך שמן קטן אחד, שהספיק ליום אחד בלבד. אבל קרה נס – השמן דלק שמונה ימים. חג חנוכה שמח.',
 'en': 'Over two thousand years ago, one small jar of pure oil was found in the Temple – enough for just one day. But a miracle happened: it burned for eight days. Happy Hanukkah.',
 'ru': 'Более двух тысяч лет назад в Храме нашли один маленький кувшин чистого масла – всего на один день. Но случилось чудо: оно горело восемь дней. Счастливой Хануки.',
 'fr': "Il y a plus de deux mille ans, on trouva au Temple une seule petite fiole d'huile pure – pour un seul jour. Mais un miracle eut lieu : elle brûla huit jours. Joyeux Hanoukka.",
}
END = {
 'he': ('חג חנוכה שמח', 'אופק את טל מנופים', 'מנוף סל להדלקות חנוכייה · 050-9081114 · tal83.com'),
 'en': ('Happy Hanukkah', 'Ofek et Tal Cranes', 'Basket crane for menorah lightings · +972-50-908-1114 · tal83.com'),
 'ru': ('Счастливой Хануки', 'Ofek et Tal Cranes', 'Автовышка для ханукий · +972-50-908-1114 · tal83.com'),
 'fr': ('Joyeux Hanoukka', 'Ofek et Tal Cranes', 'Nacelle pour hanoukkiot · +972-50-908-1114 · tal83.com'),
}
YEL, WHITE = (255, 206, 60), (255, 255, 255)


def font(rtl, sz):
    if rtl: return ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'Heebo.ttf'), sz)
    f = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'OpenSans.ttf'), sz)
    try: f.set_variation_by_name('Bold')
    except Exception: pass
    return f


def txt(d, xy, s, sz, fill, rtl, alpha=255):
    kw = dict(direction='rtl', language='he') if rtl else {}
    f = font(rtl, sz)
    while d.textlength(s, font=f, **kw) > 980 and sz > 26: sz -= 2; f = font(rtl, sz)
    d.text(xy, s, font=f, fill=fill + (alpha,), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0, alpha), **kw)


def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)


def cam(img, p, move):
    iw, ih = img.size
    p = ease(p)
    if move == 'craneup':  z, cy = 1.18, .62 - .22 * p      # tilt/crane up from crowd to basket
    elif move == 'pushin': z, cy = 1.0 + .22 * p, .42
    elif move == 'macro':  z, cy = 1.05 + .15 * p, .45
    else:                  z, cy = 1.30 - .30 * p, .50       # pull-back reveal
    cw, ch = iw / z, ih / z
    x0 = (iw - cw) / 2; y0 = min(max(0, cy * ih - ch / 2), ih - ch)
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BICUBIC)


GRAIN = [Image.effect_noise((W // 2, H // 2), 18).resize((W, H)).convert('L') for _ in range(6)]


def frame(imgs, t, lang):
    out = None
    for (a, b, name, mv) in SHOTS:
        if a <= t <= b:
            fr = cam(imgs[name], (t - a) / (b - a), mv)
            fl = 1 + (.05 if mv == 'macro' else .03) * math.sin(t * 19) + .02 * math.sin(t * 7.7)   # firelight flicker
            fr = ImageEnhance.Brightness(fr).enhance(fl)
            al = 1.0 if a == 0 else min(1.0, (t - a) / .6)
            out = fr if out is None else Image.blend(out, fr, al)
    out = ImageEnhance.Contrast(out).enhance(1.06)
    g = GRAIN[int(t * FPS) % len(GRAIN)]
    out = Image.composite(out, ImageEnhance.Brightness(out).enhance(.94), g.point(lambda v: 255 if v > 128 else 215))
    img = out.convert('RGBA'); d = ImageDraw.Draw(img)
    # film letterbox at start, opening fade from black
    if t < 1.0:
        img.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - t)))))
    rtl = lang == 'he'
    if t > 13.2:
        a = int(255 * ease((t - 13.2) / .8))
        shade = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
        for y in range(1150, H): sd.line([(0, y), (W, y)], fill=(0, 0, 0, int(min(200, (y - 1150) * .5) * a / 255)))
        img.alpha_composite(shade); d = ImageDraw.Draw(img)
        e = END[lang]
        txt(d, (W / 2, 1420), e[0], 104, YEL, rtl, a)
        txt(d, (W / 2, 1540), e[1], 58, WHITE, rtl, a)
        txt(d, (W / 2, 1620), e[2], 38, WHITE, rtl, a)
    d.text((W - 40, H - 40), 'הדמיה' if rtl else 'AI', font=font(rtl, 26), fill=(230, 230, 230, 170), anchor='rs',
           **(dict(direction='rtl', language='he') if rtl else {}))
    return img.convert('RGB')


async def _tts(text, voice, path):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate='-4%').save(path)


def main():
    lang, out = sys.argv[1], sys.argv[2]
    imgs = {s[2]: Image.open(os.path.join(PRO, s[2])).convert('RGB') for s in SHOTS}
    tmp = tempfile.mkdtemp()
    for i in range(int(DUR * FPS)):
        frame(imgs, i / FPS, lang).save(os.path.join(tmp, '%04d.jpg' % i), quality=90)
    vo = os.path.join(tmp, 'vo.mp3')
    try:
        asyncio.run(_tts(NARR[lang], VOICE[lang], vo)); has = True
    except Exception as e:
        print('tts failed', e); has = False
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, '%04d.jpg')]
    if has:
        cmd += ['-i', vo, '-filter_complex', '[1:a]adelay=1200|1200,apad,volume=1.5[a]', '-map', '0:v', '-map', '[a]']
    else:
        cmd += ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-map', '0:v', '-map', '1:a']
    cmd += ['-t', str(DUR), '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', out]
    subprocess.run(cmd, check=True)
    print(out)


if __name__ == '__main__':
    main()
