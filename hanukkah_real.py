"""27.11 Tal: realistic Hanukkah video – 3 AI stills (Jerusalem, basket crane, giant hanukkiah) with cinematic
camera moves, candle-glow flicker, blessing, original bell tune, brand bar. Label 'הדמיה'.
python hanukkah_real.py img1 img2 img3 out.mp4"""
import sys, os, math, subprocess, tempfile
from PIL import Image, ImageDraw, ImageEnhance
import hanukkah as hk

W, H, FPS = 1080, 1920, 30
SHOTS = [(0.0, 4.5), (4.0, 9.0), (8.5, 14.0)]   # overlapping for crossfades
DUR = 14.0


def shot(img, p, mode):
    """p 0..1 → cropped/zoomed frame."""
    if mode == 'in':   z, cx, cy = 1.0 + .18 * p, .5, .42
    elif mode == 'up': z, cx, cy = 1.12 + .10 * p, .5, .55 - .15 * p
    else:              z, cx, cy = 1.25 - .25 * p, .5, .5
    iw, ih = img.size
    cw, ch = iw / z, ih / z
    x0 = min(max(0, cx * iw - cw / 2), iw - cw); y0 = min(max(0, cy * ih - ch / 2), ih - ch)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)


def frame(imgs, t):
    modes = ['in', 'up', 'out']
    out = None
    for (a, b), im, m in zip(SHOTS, imgs, modes):
        if a <= t <= b:
            fr = shot(im, (t - a) / (b - a), m)
            fr = ImageEnhance.Brightness(fr).enhance(1 + .04 * math.sin(t * 17) + .03 * math.sin(t * 7.3))  # candle flicker
            alpha = min(1.0, (t - a) / .5) if a > 0 else 1.0
            out = fr if out is None else Image.blend(out, fr, alpha)
    img = out.convert('RGBA'); d = ImageDraw.Draw(img)
    if t < 4.2: hk.text(d, (W / 2, 230), 'חנוכה בירושלים', 96, hk.YEL, stroke=5)
    if t < 4.2 and t > 1.2: hk.text(d, (W / 2, 345), 'מנוף סל מדליק את החנוכייה הגדולה', 54, hk.WHITE, stroke=3)
    if 4.6 < t < 8.8:
        hk.text(d, (W / 2, 1400), "בָּרוּךְ אַתָּה ה' אֱלֹקֵינוּ מֶלֶךְ הָעוֹלָם", 52, hk.WHITE, stroke=3)
        hk.text(d, (W / 2, 1478), 'אֲשֶׁר קִדְּשָׁנוּ בְּמִצְוֹתָיו וְצִוָּנוּ', 52, hk.WHITE, stroke=3)
        hk.text(d, (W / 2, 1560), 'לְהַדְלִיק נֵר חֲנֻכָּה', 66, hk.YEL, stroke=4)
        hk.text(d, (W / 2, 260), 'רתמה · קסדה · מפעיל מוסמך', 56, hk.WHITE, stroke=3)
    if t > 9.2:
        hk.text(d, (W / 2, 300), 'חנוכה שמח!', 130, hk.YEL, stroke=6)
        hk.text(d, (W / 2, 430), 'מנוף סל להדלקות חנוכייה ענקית', 58, hk.WHITE, stroke=3)
        hk.text(d, (W / 2, 510), 'עיריות · ישיבות · מוסדות · אירועים', 46, hk.WHITE, stroke=3)
    hk.text(d, (W - 90, H - 160), 'הדמיה', 30, (235, 235, 235), stroke=2)
    d.rectangle([0, H - 120, W, H], fill=(10, 10, 10)); d.rectangle([0, H - 126, W, H - 120], fill=hk.YEL)
    hk.text(d, (W / 2, H - 60), 'אופק את טל מנופים · tal83.com · 050-9081114', 46, hk.WHITE)
    av = Image.open(os.path.join(hk.ROOT, 'assets', 'mascot_round.png')).convert('RGBA').resize((170, 170))
    img.alpha_composite(av, (20, H - 300))
    return img.convert('RGB')


def main():
    imgs = [Image.open(p).convert('RGB') for p in sys.argv[1:4]]
    out = sys.argv[4]
    tmp = tempfile.mkdtemp()
    for i in range(int(DUR * FPS)):
        frame(imgs, i / FPS).save(os.path.join(tmp, '%04d.jpg' % i), quality=90)
    hk.DUR = DUR; mus = os.path.join(tmp, 'm.wav'); hk.melody(mus, seed=1225)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, '%04d.jpg'), '-i', mus,
                    '-filter_complex', '[1:a]volume=0.9,afade=t=out:st=%s:d=1.5[a]' % (DUR - 1.5), '-map', '0:v', '-map', '[a]',
                    '-t', str(DUR), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', out], check=True)
    print(out)


if __name__ == '__main__':
    main()
