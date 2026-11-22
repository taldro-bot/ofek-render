import sys
"""Daily remix generator — makes one NEW unique video job per run from our own material.
Combines: topic template x city x photos x language x hook (render.py rotates hooks by id).
State in state/used.json so no combination repeats. Output: jobs/<id>.json, prints the id."""
import json, os, random, datetime, re, urllib.request
from kinds import QUESTION, QUIZ, TIP, FOREIGN, MACHINES, FOREIGN_LANGS, REGS, REGS_AR

U = 'https://www.tal83.com/img/'
FIELD = ['aerial-lift-rental-shoham', 'aerial-platform-rental-nes-ziona', 'aerial-work-platform-rental-petah-tikva',
         'aerial-work-platforms-tree-trimming-field-story', 'basket-crane-rental-price-factors', 'boom-lift-rental-yehud',
         'boom-lift-tree-pruning-safety-electrical-lines', 'boom-towers', 'bucket-crane-petah-tikva', 'bucket-crane-rental-yehud',
         'bucket-truck-crane-hadera', 'bucket-truck-services-nes-ziona', 'cherry-picker-crane-rental-guide',
         'crane-basket-safety-tip-leveling-slopes', 'crane-basket-safety-tip-power-lines', 'crane-hand-signals-guide',
         'crane-signalman-safety-guidelines', 'ground-spotter-height-safety-tip', 'hero-boom', 'manof-sal-guide-and-ordering',
         'palm-trim', 'quick-response-access-solutions-gedera', 'risk-assessment-safety-tip-height-work',
         'safety-tip-height-training-anchor-point', 'safety-tip-height-training-never-stand-under-load',
         'safety-tip-working-at-height-basket-harness', 'sign-install', 'street-reach', 'tree-lift-ramat-aviv-idan', 'truck-street',
         'working-at-height-course-petah-tikva', 'working-at-height-safety-equipment-checklist',
         'working-at-height-safety-tip-ground-inspection-before-setup']
CITYIMG = sorted(f for f in os.listdir('assets/cities'))
CITIES = ['ירושלים', 'תל אביב', 'חיפה', 'ראשון לציון', 'פתח תקווה', 'אשדוד', 'נתניה', 'באר שבע', 'בני ברק', 'חולון', 'רמת גן',
          'רחובות', 'אשקלון', 'בת ים', 'בית שמש', 'כפר סבא', 'הרצליה', 'חדרה', 'מודיעין', 'נצרת', 'לוד', 'רמלה', 'רעננה', 'ראש העין',
          'הוד השרון', 'גבעתיים', 'קריית גת', 'נהריה', 'עפולה', 'אילת', 'באר יעקב', 'זכרון יעקב', 'צפת', 'מצפה רמון', 'דימונה',
          'ערד', 'כרמיאל', 'טבריה', 'עכו', 'קריית שמונה', 'שדרות', 'נתיבות', 'אופקים', 'יבנה', 'נס ציונה', 'קריית אונו', 'יקנעם',
          'אבו גוש', 'יהוד', 'שוהם', 'גדרה', 'אור יהודה', 'גבעת שמואל', 'אלעד', 'טירה', 'טייבה', 'אום אל פחם', 'סחנין']
VIRAL = [  # 21.11 viral formulas: "you" hook in first 2s, open question -> comments, share trigger, loop ending
    ('אל תזמינו מנוף ב{c} לפני שאתם יודעים את זה', ['אל תזמינו מנוף לפני שאתם יודעים את זה.', 'רוב האנשים מודדים מהקיר. זו טעות.', 'מודדים מהמדרכה, ומוסיפים שלושה עד ארבעה מטר.', 'שלחו את זה למי שבונה עכשיו. ולפני שמזמינים מנוף –']),
    ('נחשו כמה זה שוקל? ב{c}', ['נחשו כמה זה שוקל. כתבו בתגובות לפני הסוף.', 'מזגן גדול, דוד מלא, או משטח בלוקים?', 'משטח בלוקים שוקל בערך טון וחצי.', 'צדקתם? תכתבו. ועכשיו – נחשו כמה זה שוקל.']),
    ('מה הייתם עושים פה? ב{c}', ['אתם המנופאי. חוט חשמל מעל הראש. מה עושים?', 'מרימים בכל זאת, או עוצרים?', 'תשובה נכונה: עוצרים, ומודדים מרחק ביטחון.', 'כתבו בתגובות מה הייתם עושים. אתם המנופאי.']),
    ('את זה כולם עושים לא נכון', ['את זה כמעט כולם עושים לא נכון.', 'עומדים מתחת למטען "רק לשנייה".', 'שנייה אחת זה כל מה שצריך כדי שיקרה אסון.', 'תשלחו את זה לחבר מהעבודה. כי כמעט כולם –']),
    ('ככה נראה יום של מנופאי ב{c}', ['ככה נראה יום שלם שלי במנוף, בפחות מחצי דקה.', 'בוקר: בדיקת שטח, תמיכות, וחשמל.', 'צהריים: הנפה אחרי הנפה, בלי הפתעות.', 'שמרו את זה לפני שאתם מזמינים מנוף. ככה נראה יום –']),
    ('הלקוח אמר לי: "אין מצב שזה עולה"', ['הלקוח אמר לי: אין מצב שזה עולה לגג.', 'מטר ממרפסת, עץ באמצע, וחוטים מעל.', 'שעה אחרי – זה היה למעלה.', 'גם אצלכם אומרים אין מצב? תתייגו מישהו. כי הלקוח אמר לי –']),
]
HE = [  # (title, lines) — {c} = city
    ('מנוף סל ב{c} – ככה עושים את זה נכון', ['קיבלנו קריאה מ{c}.', 'מודדים גובה ומרחק מהמדרכה, לא מהקיר.', 'מוסיפים שלושה עד ארבעה מטר ביטחון.', 'בודקים חוטי חשמל ומקום לתמיכות.', 'צריכים מנוף ב{c}? מתקשרים לטל.']),
    ('3 טעויות לפני שמזמינים מנוף ב{c}', ['טעות ראשונה: לא שומרים חניה למנוף.', 'טעות שנייה: לא בודקים חוטי חשמל מעל.', 'טעות שלישית: לא יודעים כמה המטען שוקל.', 'בדיקה קטנה לפני – חוסכת שעות ביום העבודה.', 'אופק את טל מנופים, גם ב{c}.']),
    ('כמה זמן לוקחת הנפה ב{c}?', ['הגענו, פתחנו תמיכות, ובדקנו את השטח.', 'הנפה רגילה לוקחת פחות ממה שחושבים.', 'מה שלוקח זמן זה ההכנה. ועליה לא מתפשרים.', 'שעתיים של עבודה בטוחה, בלי הפתעות.', 'רוצים לתאם ב{c}? דברו עם טל.']),
    ('עבודה בגובה ב{c} – בלי פיגום', ['שלט, חזית, תאורה או גיזום ב{c}?', 'מנוף סל מגיע, נפתח ועובד תוך דקות.', 'רתמה, קסדה, ומשגיח קרקע למטה.', 'בלי פיגום, בלי בלגן, בלי לחסום יום שלם.', 'אופק את טל מנופים – עובדים בגובה, בבטחה.']),
    ('מה בודק מנופאי ותיק לפני הנפה ב{c}', ['קרקע: לא שוקעת, לא חלולה, בלי מכסה ביוב.', 'חשמל: מרחק ביטחון מכל קו.', 'רוח: מעל מהירות מסוימת – לא מניפים.', 'מטען: יודעים כמה שוקל, ובאיזה מרחק.', 'ככה עובדים ב{c} וככה עובדים בכל הארץ.']),
    ('גיזום עץ גבוה ב{c}', ['עץ גבוה ליד הבית ב{c}?', 'מנוף סל מעלה את הגוזם בדיוק למקום.', 'מורידים ענפים בשליטה, בלי לפגוע בגג.', 'הלקוח רק מכין קפה. אנחנו עושים את השאר.', 'אופק את טל מנופים, שירות בכל הארץ.']),
    ('התקנת מזגן לגג ב{c}', ['מזגן גדול, גג גבוה, מדרגות צרות?', 'מנוף זרוע מרים אותו מעל הבניין.', 'בלי לסחוב, בלי לשרוט קירות.', 'דקות של הנפה במקום שעות של סבל.', 'צריכים ב{c}? טל מגיע.']),
    ('דוד שמש חדש ב{c}', ['דוד שמש חדש עולה לגג ב{c}.', 'מורידים את הישן, מעלים את החדש.', 'רצועות תקינות, וו נעול, אף אחד מתחת למטען.', 'עבודה נקייה ומהירה.', 'אופק את טל מנופים – 050-9081114.']),
]
OTHER = {
    'ar': ('رافعة في كل البلاد', ['وصلنا اليوم إلى موقع عمل جديد.', 'نقيس الارتفاع والمسافة من الرصيف وليس من الحائط.', 'نفحص أسلاك الكهرباء ومكان الأرجل الداعمة.', 'عمل آمن، سريع ونظيف.', 'أوفيك وطال للرافعات – نصل إليكم.'], 'ar-SA-HamedNeural'),
    'ru': ('Автовышка по всему Израилю', ['Сегодня мы на новом объекте.', 'Высоту и вылет меряем от тротуара, а не от стены.', 'Проверяем провода и место для опор.', 'Безопасно, быстро и аккуратно.', 'Офек и Таль — приедем к вам.'], 'ru-RU-DmitryNeural'),
    'en': ('Cranes all over Israel', ['Today we are on a new job site.', 'We measure height and reach from the sidewalk, not the wall.', 'We check power lines and room for the outriggers.', 'Safe, fast and clean work.', 'Ofek et Tal Cranes — we come to you.'], 'en-US-GuyNeural'),
    'fr': ('Grue partout en Israël', ["Aujourd'hui, nouveau chantier.", "On mesure la hauteur depuis le trottoir, pas depuis le mur.", "On vérifie les lignes électriques et la place des stabilisateurs.", "Un travail sûr, rapide et propre.", "Ofek et Tal Grues — on vient chez vous."], 'fr-FR-HenriNeural'),
    'hi': ('पूरे इज़राइल में क्रेन', ['आज हम एक नई साइट पर हैं।', 'ऊँचाई और दूरी फुटपाथ से नापते हैं, दीवार से नहीं।', 'बिजली के तार और सपोर्ट की जगह जाँचते हैं।', 'सुरक्षित, तेज़ और साफ़ काम।', 'ओफ़ेक एट ताल क्रेन्स — हम आपके पास आते हैं।'], 'hi-IN-MadhurNeural'),
    'si': ('ඊශ්‍රායලය පුරා ක්‍රේන්', ['අද අපි අලුත් වැඩබිමක.', 'උස සහ දුර මනින්නේ පදික වේදිකාවේ සිට, බිත්තියෙන් නොවේ.', 'විදුලි රැහැන් සහ ආධාරක ඉඩ පරීක්ෂා කරමු.', 'ආරක්ෂිත, ඉක්මන් සහ පිරිසිදු වැඩ.', 'ඔෆෙක් ඇට් ටාල් ක්‍රේන්ස් — අපි ඔබ වෙත එන්නෙමු.'], 'si-LK-SameeraNeural'),
}
LANG_CYCLE = ['he', 'he', 'ar', 'he', 'ru', 'he', 'en', 'he', 'fr', 'he', 'hi', 'he', 'si']


def main():
    os.makedirs('state', exist_ok=True)
    sp = 'state/used.json'
    st = json.load(open(sp)) if os.path.exists(sp) else {'n': 0, 'used': []}
    n = st['n']; lang = LANG_CYCLE[n % len(LANG_CYCLE)]
    mach = os.environ.get('FORCE_MACH') or MACHINES[n % len(MACHINES)]   # 21.11: FORCE_MACH=regs to batch one kind
    if mach == 'foreign': lang = FOREIGN_LANGS[(n // len(MACHINES)) % len(FOREIGN_LANGS)]
    elif mach in ('question', 'quiz', 'tip', 'regs'): lang = 'he'
    if os.environ.get('FORCE_LANG'): lang = os.environ['FORCE_LANG']   # 21.11: e.g. FORCE_MACH=regs FORCE_LANG=ar
    rnd = random.Random(n * 7919 + 17)
    day = datetime.date.today().strftime('%y%m%d')
    base = 'r%s%03d' % (day, n % 1000)
    jid = base if lang == 'he' else '%s-%s' % (lang, base)
    key = None
    for _ in range(500):
        t = rnd.randrange(len(HE)); c = rnd.randrange(len(CITIES))
        k = '%s|%d|%d' % (lang, t, c)
        if k not in st['used']: key = k; break
    if key is None:  # never ends: everything used -> start a new cycle (new photos/hooks make it new again)
        st['used'] = [u for u in st['used'] if not u.startswith(lang + '|')]; key = k
    photos = rnd.sample(FIELD, 3)
    rnd.shuffle(photos)
    pics = [U + p + '.jpg' for p in photos]
    pics.insert(0, 'assets/cities/' + rnd.choice(CITYIMG))   # viral: strongest image = first frame
    if mach in ('question', 'quiz', 'tip', 'foreign', 'regs'):   # 21.11 content machines
        if mach == 'foreign': title, lines = FOREIGN[lang]; lines = list(lines); rnd.shuffle(lines[1:4])
        else:
            pool = REGS_AR if (lang == 'ar' and mach == 'regs') else {'question': QUESTION, 'quiz': QUIZ, 'tip': TIP, 'regs': REGS}[mach]; uk = st.setdefault('k_' + mach + ('_ar' if pool is REGS_AR else ''), [])
            if mach == 'tip':   # 22.11 Tal: the tip machine dubs the real daily tips from tal83 (falls back to the fixed TIP list)
                try:
                    live = json.loads(urllib.request.urlopen(urllib.request.Request('https://www.tal83.com/api/tips.json', headers={'User-Agent': 'Mozilla/5.0 ofek-remix'}), timeout=30).read())
                    ud = st.setdefault('tips_live', [])
                    cand = [t for t in live if t.get('title') and t.get('tip') and t['title'] not in ud]
                    if cand:
                        t = cand[0]; ud.append(t['title']); del ud[:-200]
                        sents = [x.strip() for x in re.split(r'(?<=[.!?])\s+|,\s+(?=כדי|אחרת|כי)', t['tip']) if x.strip()]
                        pool = [('טיפ יומי: ' + t['title'], ['טיפ יומי מאופק את טל.', t['title'] + '.'] + sents + ['טיפ ביום – שומר עליכם. אופק את טל מנופים.'])]; uk = []
                except Exception as e: print('live tips:', e, file=sys.stderr)
            free = [i for i in range(len(pool)) if i not in uk] or list(range(len(pool)))
            if len(free) == len(pool): uk.clear()
            i = rnd.choice(free); uk.append(i); title, lines = pool[i]; lines = list(lines)
        voice = OTHER[lang][2] if lang in OTHER else 'he-IL-AvriNeural'
        job = {'id': jid, 'title': title, 'lines': lines, 'photos': pics, 'lang': lang, 'voice': voice, 'rate': '+4%', 'presenter': True, 'kind': mach}
        json.dump(job, open('jobs/%s.json' % jid, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        st['n'] = n + 1; json.dump(st, open(sp, 'w'), ensure_ascii=False); print(jid); return
    art = None
    if lang == 'he' and n % 3 == 1:  # every 3rd Hebrew video: remix one of our articles/tips
        try:
            posts = json.loads(urllib.request.urlopen(urllib.request.Request('https://www.tal83.com/blog-archive.json', headers={'User-Agent': 'Mozilla/5.0 ofek-remix'}), timeout=30).read())
            used_a = set(st.get('arts', []))
            cand = [p for p in posts if p.get('slug') not in used_a and re.search('[\u0590-\u05FF]', p.get('title', ''))]
            if not cand: st['arts'] = []; cand = [p for p in posts if re.search('[\u0590-\u05FF]', p.get('title', ''))]
            art = rnd.choice(cand)
            txt = re.sub(r'<[^>]+>', ' ', art.get('html', '')); txt = re.sub(r'\s+', ' ', txt)
            sents = [s.strip() for s in re.split(r'(?<=[.!?])\s', txt) if 25 <= len(s.strip()) <= 130 and not re.search(r'http|@|\d{3}-', s)]
            if len(sents) < 4: art = None
            else:
                k0 = rnd.randrange(max(1, len(sents) - 4)); lines = sents[k0:k0 + 4] + ['המאמר המלא באתר טל שמונים ושלוש.']
                title = art['title'][:90]; voice = 'he-IL-AvriNeural'; st.setdefault('arts', []).append(art['slug'])
        except Exception as e:
            print('article skip', e, file=__import__('sys').stderr); art = None
    if art is not None:
        pass
    elif lang == 'he' and n % 3 != 2:
        vt = rnd.randrange(len(VIRAL)); title, lines = VIRAL[vt]; city = CITIES[c]
        title = title.format(c=city); lines = [x.format(c=city) for x in lines]; voice = 'he-IL-AvriNeural'; key = key + '|v%d' % vt
    elif lang == 'he':
        title, lines = HE[t]; city = CITIES[c]
        title = title.format(c=city); lines = [x.format(c=city) for x in lines]; voice = 'he-IL-AvriNeural'
    else:
        title, lines, voice = OTHER[lang]; lines = list(lines)
        rnd.shuffle(lines[1:3])
    job = {'id': jid, 'title': title, 'lines': lines, 'photos': pics, 'lang': lang, 'voice': voice, 'rate': '+4%', 'presenter': True}
    json.dump(job, open('jobs/%s.json' % jid, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    st['used'].append(key); st['n'] = n + 1
    json.dump(st, open(sp, 'w'), ensure_ascii=False)
    print(jid)


if __name__ == '__main__':
    main()
