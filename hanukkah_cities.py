"""27.11 Tal: Hanukkah slideshow per night × language (he/ru/fr/en) from our city image bank (assets/cities),
mini hanukkiah with N candles lit, blessing (he), safety line, brand bar, original bell tune.
python hanukkah_cities.py N LANG out.mp4"""
import sys, os, math, subprocess, tempfile
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
import hanukkah as hk

W, H, FPS, PER, DUR = 1080, 1920, 30, 3.0, 13.0
CITY = os.path.join(hk.ROOT, 'assets', 'cities')
POOL = ['tal-jlm-night2.jpg', 'tal-ta-night1.jpg', 'haifa-bahai.jpg', 'jlm-jaffa-gate.jpg', 'tal-jlm-night4.jpg',
        'tal-ta-tayelet-night.jpg', 'tal-haifa-carmel.jpg', 'jaffa-clock.jpg', 'tal-jlm-old.jpg', 'tal-ta-night3.jpg',
        'haifa.jpg', 'tlv-port.jpg', 'jerusalem.png', 'telaviv.png', 'tiberias-promenade.jpg', 'safed-alleys.jpg',
        'acre-port.jpg', 'tal-bneibrak-night.jpg', 'netanya.jpg', 'beersheba.jpg', 'jlm-mahane-yehuda.jpg', 'tlv-round-tower.jpg']
T = {
 'he': dict(night=[n + ' של חנוכה' for n in hk.NIGHT], happy='חנוכה שמח!', sub='מנוף סל להדלקות חנוכייה ענקית – בכל הארץ',
            safe='רתמה · קסדה · מפעיל מוסמך', brand='אופק את טל מנופים · tal83.com · 050-9081114', rtl=True),
 'en': dict(night=['Hanukkah – night %d' % i for i in range(1, 9)], happy='Happy Hanukkah!',
            sub='Basket crane for giant menorah lighting – all over Israel', safe='Harness · Helmet · Certified operator',
            brand='Ofek et Tal Cranes · tal83.com · +972-50-908-1114', rtl=False),
 'ru': dict(night=['Ханука – свеча %d' % i for i in range(1, 9)], happy='Счастливой Хануки!',
            sub='Автовышка для зажжения большой ханукии – по всему Израилю', safe='Страховка · Каска · Сертифицированный оператор',
            brand='Ofek et Tal Cranes · tal83.com · +972-50-908-1114', rtl=False),
 'fr': dict(night=['Hanoukka – bougie %d' % i for i in range(1, 9)], happy='Joyeux Hanoukka !',
            sub='Nacelle pour allumer la grande hanoukkia – partout en Israël', safe='Harnais · Casque · Opérateur certifié',
            brand='Ofek et Tal Cranes · tal83.com · +972-50-908-1114', rtl=False),
}


def txt(d, xy, s, sz, fill, rtl, stroke=3, maxw=1000):
    fp = hk.FONT if rtl else os.path.join(hk.ROOT, 'assets', 'fonts', 'OpenSans.ttf')
    def mk(z):
        ft = ImageFont.truetype(fp, z)
        if not rtl:
            try: ft.set_variation_by_name('Bold')
            except Exception: pass
        return ft
    f = mk(sz)
    kw = dict(direction='rtl', language='he') if rtl else {}
    while d.textlength(s, font=f, **kw) > maxw and sz > 28:
        sz -= 2; f = mk(sz)
    d.text(xy, s, font=f, fill=fill, anchor='mm', stroke_width=stroke, stroke_fill=(0, 0, 0), **kw)


def mini_hanukkiah(n, t):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    hk.hanukkiah(d)
    for k, i in enumerate([4] + [8 - j for j in range(n)]):
        hk.flame(lay, hk.ARM[i], hk.HTOP - (60 if i == 4 else 0) - 70, t, k)
    box = lay.crop((hk.ARM[0] - 60, hk.HTOP - 320, hk.ARM[8] + 60, hk.HBASE + 5))
    s = 420 / box.width
    return box.resize((420, int(box.height * s)), Image.LANCZOS)


def cover(path):
    im = Image.open(path).convert('RGB'); iw, ih = im.size
    s = max(W / iw, H / ih); im = im.resize((int(iw * s) + 2, int(ih * s) + 2), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H))
    return ImageEnhance.Brightness(im).enhance(.72)        # evening mood


SHADE = Image.new('RGBA', (W, H), (0, 0, 0, 0))
_sd = ImageDraw.Draw(SHADE)
for _y in range(420): _sd.line([(0, _y), (W, _y)], fill=(0, 0, 0, int(170 * (1 - _y / 420))))
for _y in range(1300, H): _sd.line([(0, _y), (W, _y)], fill=(0, 0, 0, int(150 * (_y - 1300) / (H - 1300))))


def main():
    n, lang, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    L = T[lang]
    pics = [cover(os.path.join(CITY, POOL[(n * 4 + k + {'he': 0, 'en': 1, 'ru': 2, 'fr': 3}[lang]) % len(POOL)])) for k in range(5)]
    tmp = tempfile.mkdtemp()
    for fi in range(int(DUR * FPS)):
        t = fi / FPS; k = min(int(t // PER), len(pics) - 1); p = (t % PER) / PER
        z = 1.0 + .10 * p
        im = pics[k].resize((int(W * z), int(H * z))); x, y = (im.width - W) // 2, (im.height - H) // 2
        fr = im.crop((x, y, x + W, y + H))
        if p < .15 and k > 0:
            prev = pics[k - 1].resize((int(W * 1.1), int(H * 1.1))); px, py = (prev.width - W) // 2, (prev.height - H) // 2
            fr = Image.blend(prev.crop((px, py, px + W, py + H)), fr, p / .15)
        img = fr.convert('RGBA'); d = ImageDraw.Draw(img)
        img.alpha_composite(SHADE)
        txt(d, (W / 2, 200), L['night'][n - 1], 88, hk.YEL, L['rtl'], 5)
        txt(d, (W / 2, 310), L['safe'], 52, hk.WHITE, L['rtl'])
        mh = mini_hanukkiah(n, t); img.alpha_composite(mh, ((W - mh.width) // 2, 820)); d = ImageDraw.Draw(img)
        if lang == 'he' and 2.0 < t < 8.5:
            txt(d, (W / 2, 1390), "בָּרוּךְ אַתָּה ה' אֱלֹקֵינוּ מֶלֶךְ הָעוֹלָם", 52, hk.WHITE, True)
            txt(d, (W / 2, 1468), 'אֲשֶׁר קִדְּשָׁנוּ בְּמִצְוֹתָיו וְצִוָּנוּ', 52, hk.WHITE, True)
            txt(d, (W / 2, 1550), 'לְהַדְלִיק נֵר חֲנֻכָּה', 66, hk.YEL, True, 4)
        if t >= (8.5 if lang == 'he' else 3.0):
            txt(d, (W / 2, 1420), L['happy'], 120, hk.YEL, L['rtl'], 6)
            txt(d, (W / 2, 1545), L['sub'], 50, hk.WHITE, L['rtl'])
        txt(d, (W - 90, H - 160), 'הדמיה' if lang == 'he' else 'AI', 30, (235, 235, 235), lang == 'he', 2)
        d.rectangle([0, H - 120, W, H], fill=(10, 10, 10)); d.rectangle([0, H - 126, W, H - 120], fill=hk.YEL)
        txt(d, (W / 2, H - 60), L['brand'], 44, hk.WHITE, L['rtl'], 0)
        av = Image.open(os.path.join(hk.ROOT, 'assets', 'mascot_round.png')).convert('RGBA').resize((170, 170))
        img.alpha_composite(av, (20, H - 300))
        img.convert('RGB').save(os.path.join(tmp, '%04d.jpg' % fi), quality=88)
    hk.DUR = DUR; mus = os.path.join(tmp, 'm.wav'); hk.melody(mus, seed=100 + n)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, '%04d.jpg'), '-i', mus,
                    '-filter_complex', '[1:a]volume=0.9,afade=t=out:st=%s:d=1.5[a]' % (DUR - 1.5), '-map', '0:v', '-map', '[a]',
                    '-t', str(DUR), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', out], check=True)
    print(out)


if __name__ == '__main__':
    main()
