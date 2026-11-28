#!/usr/bin/env python3
"""Ofek et Tal - short vertical video renderer.

Usage: python3 render.py job.json
job.json:
{
  "id": "2026-11-01-a",
  "title": "כותרת קצרה",
  "lines": ["משפט ראשון.", "משפט שני.", ...],     # mini article, 4-10 short sentences
  "photos": ["photos/a.jpg", "photos/b.jpg", ...],
  "voice": "he-IL-HilaNeural",                      # optional
  "music": "assets/music/track.mp3"                 # optional, played quietly
}
Output: out/<id>.mp4 (1080x1920, 30fps) + out/<id>.srt
Voice: edge-tts (free). If unavailable, renders silently with estimated timing.
"""
import json, os, subprocess, sys, shutil, math, asyncio

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(ROOT, 'assets', 'fonts')
LOGO = os.path.join(ROOT, 'assets', 'logo.png')
BADGE = os.path.join(ROOT, 'assets', 'logo_badge.png')
PHONE, SITE = '050-9081114', 'tal83.com'


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def tts(lines, voice, tmp, rate='+12%'):
    """Return list of (mp3 path or None, seconds, word_starts) - word_starts relative to line start."""
    res = []
    try:
        import edge_tts

        async def one(text, path):
            try:
                c = edge_tts.Communicate(text, voice, rate=rate, pitch='+3Hz', boundary='WordBoundary')
            except TypeError:
                c = edge_tts.Communicate(text, voice, rate=rate, pitch='+3Hz')
            starts = []
            with open(path, 'wb') as f:
                async for ch in c.stream():
                    if ch['type'] == 'audio':
                        f.write(ch['data'])
                    elif ch['type'] == 'WordBoundary':
                        starts.append(ch['offset'] / 1e7)
            return starts
        for i, t in enumerate(lines):
            p = os.path.join(tmp, 'v%02d.mp3' % i)
            starts = asyncio.run(one(t, p))
            d = dur(p) + 0.25
            res.append((p, d, word_times(t, d, starts)))
        return res
    except Exception as e:  # offline / blocked: silent with estimated timing
        print('TTS unavailable, silent render:', str(e)[:120])
        out = []
        for t in lines:
            d = max(2.2, len(t.split()) / 2.4 + 0.4)
            out.append((None, d, word_times(t, d, [])))
        return out


def word_times(text, d, starts):
    """Start time of each space-separated token; use TTS boundaries when counts match, else spread by length."""
    toks = text.split()
    if len(starts) == len(toks):
        return starts
    total = sum(len(w) + 1 for w in toks); acc, out = 0.0, []
    for w in toks:
        out.append((d - 0.3) * acc / total); acc += len(w) + 1
    return out


def ts(s):
    h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
    return '%d:%02d:%05.2f' % (h, m, sec)


def srt_ts(s):
    ms = int(round(s * 1000))
    return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


RLM = '\u200f'

def rtl(t):
    if not L.get('rtl', True):
        return t.strip()
    return RLM + t.strip() + RLM


HL = '&H00F0FF&'  # TikTok yellow (BGR)

# 8.11: language support (job['lang']: he default, ar). Arabic font from apt fonts-noto-core (see render.yml).
TXT = {
    'he': {'font': 'Heebo', 'voice': 'he-IL-HilaNeural', 'brand': 'אופק את טל מנופים',
           'kick': 'סרטון נוסף מבית אופק את טל מנופים', 'q': 'צריכים מנוף סל? אנחנו כאן בשבילכם',
           's': 'חייגו או שלחו וואטסאפ עכשיו'},
    'ar': {'font': 'Noto Sans Arabic', 'voice': 'ar-JO-SanaNeural', 'brand': 'أوفيك إت طال للرافعات',
           'kick': 'فيديو جديد من أوفيك إت طال للرافعات', 'q': 'تحتاجون رافعة سلة؟ نحن هنا من أجلكم',
           's': 'اتصلوا أو أرسلوا واتساب الآن'},
    'ru': {'font': 'Noto Sans', 'voice': 'ru-RU-SvetlanaNeural', 'brand': 'Офек Эт Таль — автовышки', 'rtl': False,
           'kick': 'Новое видео от Офек Эт Таль', 'q': 'Нужна автовышка? Мы здесь для вас',
           's': 'Звоните или пишите в WhatsApp прямо сейчас'},
    'en': {'font': 'Noto Sans', 'voice': 'en-US-AriaNeural', 'brand': 'Ofek At Tal Cranes', 'rtl': False,
           'kick': 'A new video from Ofek At Tal Cranes', 'q': "Need a basket crane? We're here for you",
           's': 'Call or WhatsApp us now'},
    'fr': {'font': 'Noto Sans', 'voice': 'fr-FR-HenriNeural', 'brand': 'Ofek & Tal – Grues', 'rtl': False,
           'kick': 'Une nouvelle vidéo de Ofek & Tal', 'q': "Besoin d'une nacelle ? On est là pour vous",
           's': 'Appelez ou écrivez sur WhatsApp'},
    'hi': {'font': 'Noto Sans Devanagari', 'voice': 'hi-IN-SwaraNeural', 'brand': 'ओफ़ेक एट ताल क्रेन्स', 'rtl': False,
           'kick': 'ओफ़ेक एट ताल क्रेन्स का नया वीडियो', 'q': 'बास्केट क्रेन या ट्रेनिंग चाहिए? हम आपके लिए हैं',
           's': 'अभी कॉल या व्हाट्सऐप करें'},
    'si': {'font': 'Noto Sans Sinhala', 'voice': 'si-LK-ThiliniNeural', 'brand': 'ඔෆෙක් ඇට් ටාල් ක්‍රේන්ස්', 'rtl': False,
           'kick': 'ඔෆෙක් ඇට් ටාල් ක්‍රේන්ස් වෙතින් අලුත් වීඩියෝවක්', 'q': 'ක්‍රේන් එකක් හෝ පුහුණුවක් ඕනෙද? අපි ඉන්නවා',
           's': 'දැන්ම අමතන්න හෝ වට්ස්ඇප් කරන්න'},
    'am': {'font': 'Noto Sans Ethiopic', 'voice': 'am-ET-MekdesNeural', 'brand': 'ኦፌክ ኤት ታል ክሬንስ', 'rtl': False,   # 28.11 Tal: Amharic
           'kick': 'ከኦፌክ ኤት ታል ክሬንስ አዲስ ቪዲዮ', 'q': 'የቅርጫት ክሬን ወይም ስልጠና ይፈልጋሉ? እኛ እዚህ ነን',
           's': 'አሁኑኑ ይደውሉ ወይም በዋትስአፕ ይጻፉ'},
}
L = TXT['he']
# 20.11 WOW: attention openers (Tal: "וואו, דבר כזה לא ראיתם, שמעתם מה קרה?") – rotated by job id
HOOKS = {
    'he': ['וואו! דבר כזה עוד לא ראיתם', 'שמעתם מה קרה בשטח?', 'תראו מה עשינו', 'רוצים לראות משהו יפה?',
           'ככה עושים את זה נכון', 'נחשו כמה זה גבוה?', 'מאחורי הקלעים של מנופאי'],
    'ar': ['واو! ما شفتوا شي هيك', 'سمعتوا شو صار بالشغل؟', 'شوفوا شو عملنا', 'هيك بنشتغل صح'],
    'ru': ['Вау! Такого вы ещё не видели', 'Слышали, что было на объекте?', 'Смотрите, что мы сделали', 'Вот как это делают правильно'],
    'fr': ["Waouh ! Vous n'avez jamais vu ça", 'Devinez ce qui s\'est passé ?', "Regardez ce qu'on a fait", 'Voilà comment les pros font'],
    'en': ["Wow! You've never seen this", 'Guess what happened on site?', 'Look what we did', 'This is how pros do it'],
    'hi': ['वाह! ऐसा आपने पहले नहीं देखा', 'देखिए हमने क्या किया', 'ऐसे होता है सही काम'],
    'si': ['වාව්! මෙහෙම දෙයක් ඔබ දැකලා නැහැ', 'අපි කළ දේ බලන්න', 'නිවැරදිව කරන්නේ මෙහෙමයි'],
    'am': ['ዋው! እንደዚህ አይታችሁ አታውቁም', 'ያደረግነውን ተመልከቱ', 'በትክክል የሚሰራው እንዲህ ነው'],
}
SUBY = 1380
MASCOT = os.path.join(ROOT, 'assets', 'mascot_round.png'); MH, MY = 470, 1160   # 21.11 round avatar, full hair
DISC = ''  # optional disclaimer shown at the start (job['disclaimer'])


def write_subs(lines, times, words, title, total, path_ass, path_srt, hook=''):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,%(F)s,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,9,4,5,60,60,0,-1
Style: Foot,%(F)s,58,&H00FFFFFF,&H00FFFFFF,&H00B05A12,&H00000000,1,0,0,0,100,100,0,0,3,30,0,2,0,0,40,-1
Style: Kick,%(F)s,54,&H0000F0FF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,3,8,60,60,330,-1
Style: Hook,%(F)s,120,&H0000F0FF,&H00FFFFFF,&H00000000,&HA0000000,1,0,0,0,100,100,0,0,1,12,6,5,60,60,0,-1
Style: Title,%(F)s,86,&H00FFFFFF,&H00FFFFFF,&H00B05A12,&H00000000,1,0,0,0,100,100,0,0,3,28,0,8,70,330,210,-1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".replace('PlayResX: %d', 'PlayResX: %d' % W).replace('PlayResY: %d', 'PlayResY: %d' % H).replace('%(F)s', L['font'])
    # 8.11: long titles (ru/en) wrap to 2 lines — shrink a bit and push the kicker below the box
    fs, kick_y = 86, None
    est = len(title) * 86 * (0.62 if L.get('rtl', True) else 0.52)
    if est > 680:
        fs = max(60, min(86, int(86 * 1360 / est)))
        kick_y = int(210 + 2 * fs * 1.25 + 80)
    ev = ['Dialogue: 0,%s,%s,Title,,0,0,0,,{\\fs%d\\fad(250,300)\\fscx70\\fscy70\\t(0,260,\\fscx100\\fscy100)}%s' % (ts(0), ts(total), fs, rtl(title))]
    ev.append('Dialogue: 0,%s,%s,Foot,,0,0,0,,%s' % (ts(0), ts(total), '{\\fs96}' + rtl(L['brand']) + '\\N{\\fs72\\fnHeebo}' + rtl('050-9081114  •  tal83.com')))
    ev.append('Dialogue: 0,%s,%s,Kick,,0,0,0,,{%s\\fad(200,300)\\fscx60\\fscy60\\t(0,220,\\fscx100\\fscy100)}%s' % (ts(0), ts(2.8), ('\\an8\\pos(540,%d)' % kick_y) if kick_y else '', rtl(L['kick'])))
    if hook:  # 20.11 WOW: punch hook in the first 1.8s – pop + shake, centred
        hk = '{\\pos(540,820)\\fscx40\\fscy40\\t(0,160,\\fscx118\\fscy118)\\t(160,260,\\fscx100\\fscy100)\\t(300,340,\\frz3)\\t(340,380,\\frz-3)\\t(380,420,\\frz0)\\fad(0,200)}'
        ev.append('Dialogue: 2,%s,%s,Hook,,0,0,0,,%s%s' % (ts(0), ts(1.8), hk, rtl(hook)))
    if DISC:
        ev.append('Dialogue: 1,%s,%s,Sub,,0,0,0,,{\\pos(540,700)\\fs46\\bord6\\fad(200,400)}%s' % (ts(0), ts(5.5), '\\N'.join(rtl(x) for x in DISC.split('|'))))
    srt = []
    for i, (t, (a, b), ws) in enumerate(zip(lines, times, words)):
        toks = t.split()
        for j in range(len(toks)):
            s0 = a + ws[j]; s1 = a + ws[j + 1] if j + 1 < len(toks) else b
            c0 = (j // 3) * 3; chunk = toks[c0:c0 + 3]
            parts = []
            for k, w in enumerate(chunk):
                if c0 + k == j:
                    parts.append('{\\c%s\\fscx80\\fscy80\\t(0,90,\\fscx122\\fscy122)\\t(90,180,\\fscx108\\fscy108)}%s{\\r}' % (HL, w))
                else:
                    parts.append(w)
            ev.append('Dialogue: 0,%s,%s,Sub,,0,0,0,,{\\pos(540,%d)}%s' % (ts(s0), ts(s1), SUBY, rtl(' '.join(parts))))
        srt.append('%d\n%s --> %s\n%s\n' % (i + 1, srt_ts(a), srt_ts(b), t))
    open(path_ass, 'w', encoding='utf-8').write(head + '\n'.join(ev) + '\n')
    open(path_srt, 'w', encoding='utf-8').write('\n'.join(srt))


def photo_clip(src, seconds, out, k):
    n = max(1, int(round(seconds * FPS)))
    m = k % 4  # 20.11 WOW: zoom in / zoom out / pan right / pan left
    z = ("min(1+0.18*on/%d,1.18)" % n) if m == 0 else ("max(1.18-0.18*on/%d,1.0)" % n) if m == 1 else "1.15"
    vf = ("[0:v]split[a][b];"
          "[a]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,boxblur=40:6,eq=brightness=-0.12[bg];"
          "[b]scale=%d:-2,zoompan=z='%s':x='%s':y='ih/2-(ih/zoom/2)':d=%d:s=%dx%d:fps=%d[fg0];"
          "[fg0]scale=%d:-2[fg];"
          "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]") % (W, H, W, H, W * 2, z, ("(iw-iw/zoom)*on/%d" % n) if m == 2 else ("(iw-iw/zoom)*(1-on/%d)" % n) if m == 3 else "iw/2-(iw/zoom/2)", n, W * 2, int(W * 2 * 0.75), FPS, W)
    # zoompan output must keep the photo's aspect; use 4:3 canvas then fit on 9:16 background
    run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-t', '%.3f' % seconds, '-i', src,
         '-filter_complex', vf, '-map', '[v]', '-r', str(FPS), '-t', '%.3f' % seconds,
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', out])


def video_clip(src, seconds, out):
    # real field footage (assets/clips/*.mp4, already 9:16) as moving B-roll; loops if short
    run(['ffmpeg', '-y', '-loglevel', 'error', '-stream_loop', '-1', '-i', src, '-an',
         '-vf', 'scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,fps=%d,format=yuv420p' % (W, H, W, H, FPS),
         '-t', '%.3f' % seconds, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', out])


def end_card(out, seconds=4.0):
    txt = os.path.join(os.path.dirname(out), 'end.ass')
    R = RLM if L.get('rtl', True) else ''
    open(txt, 'w', encoding='utf-8').write("""[Script Info]
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Q,%(F)s,84,&H00B05A12,&H00FFFFFF,&H00FFFFFF,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,40,40,0,-1
Style: P,%(F)s,120,&H00FFFFFF,&H00FFFFFF,&H002E7BF0,&H00000000,1,0,0,0,100,100,0,0,3,34,0,5,40,40,0,-1
Style: S,%(F)s,58,&H00303030,&H00FFFFFF,&H00FFFFFF,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,40,40,0,-1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:10.00,Q,,0,0,0,,{\\move(540,1020,540,960,0,350)\\fad(300,0)}%s%s%s
Dialogue: 0,0:00:00.40,0:00:10.00,P,,0,0,0,,{\\fnHeebo\\pos(540,1180)\\fscx40\\fscy40\\t(0,300,\\fscx108\\fscy108)\\t(300,450,\\fscx100\\fscy100)\\t(1300,1600,\\fscx106\\fscy106)\\t(1600,1900,\\fscx100\\fscy100)\\t(2500,2800,\\fscx106\\fscy106)\\t(2800,3100,\\fscx100\\fscy100)}%s
Dialogue: 0,0:00:00.90,0:00:10.00,S,,0,0,0,,{\\pos(540,1370)\\fad(400,0)}%s%s%s
Dialogue: 0,0:00:01.30,0:00:10.00,S,,0,0,0,,{\\pos(540,1460)\\fad(400,0)\\c&HB05A12&\\fnHeebo}%s
""".replace('%(F)s', L['font']) % (W, H, R, L['q'], R, PHONE, R, L['s'], R, SITE))
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=white:s=%dx%d:r=%d' % (W, H, FPS), '-i', LOGO,
         '-filter_complex', "[1:v]scale=%d:-2[lg];[0:v][lg]overlay=(W-w)/2:280,ass=%s:fontsdir=%s,fade=t=in:st=0:d=0.3,format=yuv420p[v]"
         % (int(W * 0.8), txt, FONT_DIR),
         '-map', '[v]', '-t', '%.2f' % seconds, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', out])


def main(job_path):
    job = json.load(open(job_path, encoding='utf-8'))
    global DISC, L
    DISC = job.get('disclaimer', '')
    L = TXT.get(job.get('lang', 'he'), TXT['he'])
    jid = job['id']; lines = job['lines']; photos = job['photos']
    tmp = os.path.join(ROOT, 'tmp', jid); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)

    single = job.get('audio')  # one Danit mp3 for title + all lines
    if single:
        D = dur(single)
        segs = [job.get('title', '')] + lines
        wts = [len(x) + 6 for x in segs]; tot = float(sum(wts))
        t, voice, times = 0.6, [], []
        for k, x in enumerate(segs):
            d = D * wts[k] / tot
            if k > 0:
                voice.append((None, d, word_times(x, d, [])))
                times.append((t, t + d - 0.05))
            t += d
        body = 0.6 + D + 0.5
    else:
        voice = tts(lines, job.get('voice') or L['voice'], tmp, job.get('rate', '+12%'))
        times, t = [], 0.6
        for _, d, _w in voice:
            times.append((t, t + d - 0.1)); t += d
        body = t + 0.5
    END = 4.0
    total = body + END

    # photos spread across body
    sc = float(job.get('scene', 2.0))  # 20.11 WOW: short scenes keep viewers watching
    n = max(1, int(body // sc)); per = body / n
    XF = 0.4
    TR = job.get('transitions') or ['smoothleft', 'zoomin', 'slideup', 'circleopen', 'smoothright', 'radial']
    clips = []
    for k in range(n):
        c = os.path.join(tmp, 'p%02d.mp4' % k)
        src = photos[k % len(photos)]
        if src.lower().endswith('.mp4'):
            video_clip(src, per + XF, c)
        else:
            photo_clip(src, per + XF, c, k)
        clips.append(c)
    e = os.path.join(tmp, 'end.mp4'); end_card(e, END + XF); clips.append(e)
    silent = os.path.join(tmp, 'silent.mp4')
    args = ['ffmpeg', '-y', '-loglevel', 'error']
    for c in clips:
        args += ['-i', c]
    fc, prev = [], '[0:v]'
    for k in range(1, len(clips)):
        out = '[x%d]' % k
        fc.append('%s[%d:v]xfade=transition=%s:duration=%.2f:offset=%.3f%s' % (prev, k, TR[(k - 1) % len(TR)], XF, k * per, out))
        prev = out
    run(args + ['-filter_complex', ';'.join(fc), '-map', prev, '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', silent])
    whooshes = [k * per - 0.15 for k in range(1, len(clips))]

    # narration track
    narr = os.path.join(tmp, 'narr.wav')
    inputs, filt = [], []
    for i, ((p, _, _w), (a, _)) in enumerate(zip(voice, times)):
        if p:
            inputs += ['-i', p]; filt.append('[%d:a]adelay=%d|%d[a%d]' % (len(inputs) // 2 - 1, a * 1000, a * 1000, i))
    if single:
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', single, '-af', 'adelay=600|600,apad', '-t', '%.2f' % total, '-ar', '44100', '-ac', '2', narr])
    elif inputs:
        k = len(filt)
        fc = ';'.join(filt) + ';' + ''.join('[a%d]' % i for i in range(k)) + 'amix=inputs=%d:normalize=0,apad,atrim=0:%.2f[out]' % (k, total)
        run(['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', fc, '-map', '[out]', narr])
    else:
        run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-t', '%.2f' % total, narr])
    # music (quiet, under the voice) + whoosh on every transition
    music = os.path.join(ROOT, job.get('music', 'assets/music/upbeat1.wav'))
    sfx = os.path.join(ROOT, 'assets', 'sfx', 'whoosh.wav')
    audio = os.path.join(tmp, 'mix.wav')
    ins = ['-i', narr]; fl = []; mixin = ['[0:a]']
    if os.path.exists(music):
        ins += ['-stream_loop', '-1', '-i', music]
        fl.append('[1:a]volume=0.26,afade=t=in:d=0.5,afade=t=out:st=%.2f:d=2[m]' % (total - 2)); mixin.append('[m]')
    if os.path.exists(sfx):
        base = len(ins) // 2 if not os.path.exists(music) else 2
        for i, w in enumerate(whooshes):
            ins += ['-i', sfx]
            fl.append('[%d:a]volume=0.55,adelay=%d|%d[w%d]' % (base + i, max(0, w) * 1000, max(0, w) * 1000, i)); mixin.append('[w%d]' % i)
    fl.append('%samix=inputs=%d:duration=first:normalize=0[o]' % (''.join(mixin), len(mixin)))
    run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fl), '-map', '[o]', '-t', '%.2f' % total, audio])

    ass = os.path.join(tmp, 'subs.ass'); srt = os.path.join(ROOT, 'out', jid + '.srt')
    hk_list = HOOKS.get(job.get('lang', 'he'), [])
    hook = job.get('hook') or ('' if job.get('nohook') or not hk_list else hk_list[sum(map(ord, jid)) % len(hk_list)])
    global SUBY
    SUBY = 1080 if job.get('presenter') else 1380
    write_subs(lines, times, [v[2] for v in voice], job.get('title', ''), body, ass, srt, hook)
    out = os.path.join(ROOT, 'out', jid + '.mp4')
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', audio, '-i', BADGE,
         '-f', 'lavfi', '-i', 'color=c=0xFFC20E:s=%dx14:r=%d' % (W, FPS),
         '-loop', '1', '-t', '%.2f' % (total if job.get('presenter') else 3), '-i', MASCOT,
         '-filter_complex', "[2:v]scale=300:-2[lg];[0:v][lg]overlay=W-w-30:30:enable='lt(t,%.2f)'[a];"
         "[a][3:v]overlay=x='-w+w*t/%.2f':y=0:shortest=1:enable='lt(t,%.2f)'[b];"
         # 20.11 WOW: Tal's cartoon pops up bottom-left, wiggles, ducks away (job 'nomascot' to skip)
         "[4:v]scale=-2:%d,format=rgba,rotate=a='0.07*sin(2*PI*2.5*t)':c=none:ow=rotw(0.12):oh=roth(0.12)[ms];" % (body, body, body, 440 if job.get('presenter') else MH)
         + (("[b][ms]overlay=x=0:y='if(lt(t,0.35),H-(H-%d)*t/0.35,%d+10*sin(2*PI*1.6*t))':eof_action=repeat:enable='lt(t,%.2f)'[c];" % (1210, 1210, body))
            if job.get('presenter') else
            ("[b][ms]overlay=x=10:y='if(lt(t,0.35),H-(H-%d)*t/0.35,if(lt(t,1.9),%d+12*sin(2*PI*2*t),%d+(H-%d)*(t-1.9)/0.3))':eof_action=pass:enable='lt(t,%s)'[c];" % (MY, MY, MY, MY, '2.2' if not job.get('nomascot') else '0'))) +
         "[c]fade=t=in:st=0:d=0.25:color=white,ass=%s:fontsdir=%s[v]" % (ass, FONT_DIR),
         '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-c:a', 'aac', '-b:a', '160k',
         '-movflags', '+faststart', '-shortest', out])
    print('done', out, '%.1fs' % dur(out))


if __name__ == '__main__':
    main(sys.argv[1])
