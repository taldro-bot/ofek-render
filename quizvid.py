"""21.11 Tal: contractor quiz video – question (Soniox voice) -> 10 s countdown with light music -> answer explained.
Languages he / ar / en. Job: {id, lang, title, lines, question, options[], answer, photo, quizvid: true}
  python3 quizvid.py new        -> creates one quiz job per language for the next quiz (state/quizvid.json) + pending
  python3 quizvid.py --job J    -> renders out/<id>.mp4 (needs audio_url + answer_url from dubrender.py)"""
import os, sys, json, random, subprocess, urllib.request, datetime
W, H = 1080, 1920
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, 'out'); TMP = '/tmp/qv'
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
FONT = {'he': 'Heebo', 'ar': 'Noto Sans Arabic', 'en': 'Heebo'}
UI = {'he': ('🧠 חידון קבלנים', 'יש לכם 10 שניות!', '✅ התשובה', 'אופק את טל מנופים · 050-9081114 · tal83.com'),
      'ar': ('🧠 مسابقة المقاولين', 'معكم 10 ثوانٍ!', '✅ الجواب', 'أوفيك وطال للرافعات · 050-9081114 · tal83.com'),
      'en': ('🧠 Contractor Quiz', 'You have 10 seconds!', '✅ The answer', 'Ofek et Tal Cranes · +972-50-9081114 · tal83.com')}

# original quizzes (facts checked against the Israeli work-at-height regulations Tal gave us)
Q = [
 {'he': ('מאיזה גובה עבודה נחשבת "עבודה בגובה"?', ['א. מטר אחד', 'ב. שני מטרים', 'ג. חמישה מטרים'], 'ב – מעל שני מטרים. מעבר לזה צריך הדרכה ואישור עבודה בגובה.'),
  'ar': ('من أي ارتفاع يُعتبر العمل عملاً في المرتفعات؟', ['أ. متر واحد', 'ب. متران', 'ج. خمسة أمتار'], 'ب – أكثر من مترين. بعد ذلك تحتاج تدريباً وتصريحاً.'),
  'en': ('From what height is it "work at height"?', ['A. 1 meter', 'B. 2 meters', 'C. 5 meters'], 'B – above 2 meters. From there you need training and a permit.')},
 {'he': ('כל כמה זמן מחדשים הדרכת עבודה בגובה?', ['א. כל שנה', 'ב. כל שנתיים', 'ג. כל חמש שנים'], 'ב – כל שנתיים. בלי חידוש, האישור לא בתוקף.'),
  'ar': ('كل كم يجب تجديد تدريب العمل في المرتفعات؟', ['أ. كل سنة', 'ب. كل سنتين', 'ج. كل خمس سنوات'], 'ب – كل سنتين. بدون تجديد التصريح غير صالح.'),
  'en': ('How often is work-at-height training renewed?', ['A. Every year', 'B. Every 2 years', 'C. Every 5 years'], 'B – every two years. Without renewal the permit is not valid.')},
 {'he': ('מה הגיל המינימלי לעבודה בגובה?', ['א. 16', 'ב. 17', 'ג. 18'], 'ג – 18. וגם הדרכה מוכרת.'),
  'ar': ('ما هو الحد الأدنى للعمر للعمل في المرتفعات؟', ['أ. 16', 'ب. 17', 'ج. 18'], 'ج – ثمانية عشر عاماً، مع تدريب معترف به.'),
  'en': ('What is the minimum age for work at height?', ['A. 16', 'B. 17', 'C. 18'], 'C – 18, plus recognized training.')},
 {'he': ('איזה מרחק שומרים מקו חשמל עד 33 קילו-וולט?', ['א. מטר אחד', 'ב. 3.25 מטר', 'ג. אין צורך'], 'ב – לפחות 3.25 מטר. בקווים גבוהים יותר – לפחות 5 מטר.'),
  'ar': ('ما المسافة من خط كهرباء حتى 33 كيلو فولت؟', ['أ. متر واحد', 'ب. ثلاثة أمتار وربع', 'ج. لا حاجة'], 'ب – على الأقل ثلاثة أمتار وربع، وخمسة أمتار للخطوط الأعلى.'),
  'en': ('How far from a power line up to 33 kV?', ['A. 1 meter', 'B. 3.25 meters', 'C. No need'], 'B – at least 3.25 meters. For higher voltage – at least 5 meters.')},
 {'he': ('איפה מחברים את הרתמה בסל של מנוף?', ['א. למעקה של הבניין', 'ב. לנקודת העיגון בסל', 'ג. לא צריך רתמה'], 'ב – רק לנקודת העיגון בתוך הסל. לעולם לא לבניין.'),
  'ar': ('أين نربط الحزام في سلة الرافعة؟', ['أ. بدرابزين المبنى', 'ب. بنقطة التثبيت في السلة', 'ج. لا حاجة للحزام'], 'ب – فقط بنقطة التثبيت داخل السلة، وليس بالمبنى أبداً.'),
  'en': ('Where do you clip the harness in a crane basket?', ['A. To the building railing', 'B. To the anchor point in the basket', 'C. No harness needed'], 'B – only to the anchor point inside the basket. Never to the building.')},
 {'he': ('מאיפה מודדים מרחק להנפה?', ['א. מהקיר של הבניין', 'ב. מהמקום שבו המנוף עומד', 'ג. מהגג'], 'ב – מהמקום שבו המנוף עומד, בדרך כלל המדרכה. ועוד 3–4 מטר ביטחון.'),
  'ar': ('من أين نقيس مسافة الرفع؟', ['أ. من حائط المبنى', 'ب. من مكان وقوف الرافعة', 'ج. من السطح'], 'ب – من مكان وقوف الرافعة، عادة الرصيف، مع ثلاثة إلى أربعة أمتار احتياط.'),
  'en': ('Where do you measure lifting reach from?', ['A. The building wall', 'B. Where the crane stands', 'C. The roof'], 'B – from where the crane stands, usually the sidewalk. Plus 3–4 meters of margin.')},
 {'he': ('באיזו זווית מציבים סולם?', ['א. 45 מעלות', 'ב. בערך 75 מעלות', 'ג. 90 מעלות'], 'ב – בערך 75 מעלות, והסולם בולט מטר מעל נקודת העלייה.'),
  'ar': ('بأي زاوية نضع السلم؟', ['أ. 45 درجة', 'ب. تقريباً 75 درجة', 'ج. 90 درجة'], 'ب – تقريباً خمسة وسبعون درجة، ويرتفع السلم متراً فوق نقطة الصعود.'),
  'en': ('At what angle do you set a ladder?', ['A. 45 degrees', 'B. About 75 degrees', 'C. 90 degrees'], 'B – about 75 degrees, extending one meter above the landing.')},
 {'he': ('מי חייב להיות למטה כשעובדים בגובה?', ['א. אף אחד', 'ב. איש קרקע', 'ג. רק בלילה'], 'ב – תמיד איש קרקע: משגיח, מתקשר וקורא לעזרה.'),
  'ar': ('من يجب أن يكون على الأرض أثناء العمل في المرتفعات؟', ['أ. لا أحد', 'ب. شخص على الأرض', 'ج. فقط في الليل'], 'ب – دائماً شخص على الأرض: يراقب ويتواصل ويطلب المساعدة.'),
  'en': ('Who must be on the ground during work at height?', ['A. Nobody', 'B. A ground person', 'C. Only at night'], 'B – always a ground person: watching, communicating, calling for help.')},
]


def run(c): subprocess.run(c, check=True)


def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())


def new_jobs():
    sp = 'state/quizvid.json'; st = json.load(open(sp)) if os.path.exists(sp) else {'n': 0}
    n = st['n']; q = Q[n % len(Q)]; day = datetime.date.today().strftime('%y%m%d')
    cities = sorted(os.listdir('assets/cities')); photo = 'assets/cities/' + random.Random(n).choice(cities)
    ids = []
    for li, lang in enumerate(['he', 'ar', 'en']):
        qu, opts, ans = q[lang]; base = 'r%s%03d' % (day, 900 + (n % 50) * 3 + li); jid = base if lang == 'he' else '%s-%s' % (lang, base)
        job = {'id': jid, 'lang': lang, 'kind': 'quizvid', 'quizvid': True, 'title': UI[lang][0].replace('🧠 ', ''),
               'lines': [qu] + opts + [UI[lang][1]], 'question': qu, 'options': opts, 'answer': ans, 'photo': photo}
        json.dump(job, open('jobs/%s.json' % jid, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); ids.append(jid)
    open('state/pending.txt', 'a').write('\n'.join(ids) + '\n'); st['n'] = n + 1; json.dump(st, open(sp, 'w')); print(' '.join(ids))


def esc(t): return t.replace('\\', '').replace('{', '(').replace('}', ')').replace('\n', '\\N')


def t2(s): h = int(s // 3600); m = int(s % 3600 // 60); return '%d:%02d:%05.2f' % (h, m, s % 60)


def render(j, qa, aa):
    from PIL import Image, ImageDraw, ImageFilter
    lang = j['lang']; F = FONT.get(lang, 'Heebo'); ui = UI[lang]
    dq, da = dur(qa), dur(aa); t_c = dq + 0.4; t_a = t_c + 10.0; T = t_a + da + 2.2
    # background: the place photo, blurred + darkened; round avatar + brand bar (no text in PIL – ASS draws all text)
    bg = Image.open(os.path.join(ROOT, j['photo'])).convert('RGB')
    s = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1)).crop((0, 0, W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(6)); bg = Image.blend(bg, Image.new('RGB', (W, H), (10, 12, 16)), 0.55)
    d = ImageDraw.Draw(bg); d.rectangle([0, H - 170, W, H], fill=(14, 14, 16)); d.rectangle([0, H - 176, W, H - 170], fill=(255, 194, 14))
    av = Image.open(os.path.join(ROOT, 'assets', 'mascot_round.png')).convert('RGBA').resize((260, 260))
    bg.paste(av, (W - 300, H - 176 - 250), av); bgp = os.path.join(TMP, 'bg.png'); bg.save(bgp)
    rtl = lang in ('he', 'ar'); al = 9 if rtl else 7
    ev = []
    def E(st, a, b, txt, tags=''): ev.append('Dialogue: 0,%s,%s,%s,,0,0,0,,%s%s' % (t2(a), t2(b), st, tags, esc(txt)))
    E('Head', 0, T, ui[0])
    E('Q', 0.2, t_a + da + 2.2, j['question'], '{\\fad(250,0)}')
    for i, o in enumerate(j['options']):
        E('Opt', 0.6 + i * 0.5, t_a, o, '{\\fad(200,0)\\pos(%d,%d)}' % (W - 90 if rtl else 90, 900 + i * 130))
    E('Sub', t_c, t_a, ui[1], '{\\fad(150,150)}')
    for k in range(10):
        E('Count', t_c + k, t_c + k + 1, str(10 - k), '{\\fad(80,120)\\t(0,900,\\fscx70\\fscy70)}')
    E('AnsHead', t_a, T, ui[2], '{\\fad(200,0)}')
    E('Ans', t_a + 0.3, T, j['answer'], '{\\fad(250,0)}')
    E('Foot', 0, T, ui[3])
    ass = os.path.join(TMP, 'q.ass')
    open(ass, 'w', encoding='utf-8').write("""[Script Info]
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Head,%s,78,&H0000C2FF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,2,8,60,60,120,-1
Style: Q,%s,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,2,8,80,80,330,-1
Style: Opt,%s,66,&H00FFFFFF,&H00FFFFFF,&H00B05A12,&H00000000,1,0,0,0,100,100,0,0,3,18,0,%d,90,90,0,-1
Style: Sub,%s,58,&H0000C2FF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,2,2,60,60,560,-1
Style: Count,%s,260,&H0000C2FF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,10,4,2,60,60,260,-1
Style: AnsHead,%s,80,&H0050D26E,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,2,2,60,60,820,-1
Style: Ans,%s,66,&H00FFFFFF,&H00FFFFFF,&H00205020,&H00000000,1,0,0,0,100,100,0,0,3,22,0,2,80,80,520,-1
Style: Foot,%s,44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,2,40,40,62,-1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (W, H, F, F, F, al, F, F, F, F, F) + '\n'.join(ev) + '\n')
    # audio: question voice -> 10 s light music + soft ticks -> answer voice (music ducked under the voices)
    from clipmix import music
    mu = os.path.join(TMP, 'music.wav'); music(mu, T + 1, random.Random(hash(j['id']) & 0xffff))
    out = os.path.join(OUT, j['id'] + '.mp4')
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-loop', '1', '-framerate', '30', '-i', bgp, '-i', qa, '-i', aa, '-i', mu,
         '-filter_complex',
         '[1:a]adelay=200|200,volume=1.6[q];[2:a]adelay=%d|%d,volume=1.6[a];'
         '[3:a]volume=0.10,volume=2.6:enable=\'between(t,%.2f,%.2f)\'[m];'
         '[q][a][m]amix=inputs=3:duration=longest:normalize=0[au];'
         '[0:v]ass=%s:fontsdir=%s,format=yuv420p[v]' % (int(t_a * 1000), int(t_a * 1000), t_c, t_a, ass, os.path.join(ROOT, 'assets', 'fonts')),
         '-map', '[v]', '-map', '[au]', '-t', '%.2f' % T, '-r', '30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '22',
         '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out])
    meta = dict(j); meta['title'] = '%s – %s | אופק את טל מנופים' % (ui[0].replace('🧠 ', ''), j['question']) if lang == 'he' else '%s – %s' % (ui[0].replace('🧠 ', ''), j['question'])
    json.dump(meta, open(os.path.join(OUT, j['id'] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    if sys.argv[1] == 'new': new_jobs()
    else:
        j = json.load(open(sys.argv[2])); qa = os.path.join(TMP, 'q.mp3'); aa = os.path.join(TMP, 'a.mp3')
        urllib.request.urlretrieve(j['audio_url'], qa); urllib.request.urlretrieve(j['answer_url'], aa); render(j, qa, aa)
