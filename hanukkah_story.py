"""27-28.11 Tal: narrate the Hanukkah city videos with the story of the oil jar (פך השמן), one part per night,
in he/en/ru/fr (edge-tts, free; male voices – never Hila). Output: media/hanukkah/narrated/hanukkah-N-LANG.mp4"""
import os, sys, asyncio, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'media', 'hanukkah', 'cities')
OUT = os.path.join(ROOT, 'media', 'hanukkah', 'narrated')
VOICE = {'he': 'he-IL-AvriNeural', 'en': 'en-US-GuyNeural', 'ru': 'ru-RU-DmitryNeural', 'fr': 'fr-FR-HenriNeural'}
FALLBACK = {'ru': 'ru-RU-SvetlanaNeural', 'fr': 'fr-FR-DeniseNeural', 'en': 'en-US-AriaNeural'}
STORY = {
 'he': ['לפני יותר מאלפיים שנה, היוונים טימאו את בית המקדש בירושלים.',
        'המכבים, מעטים מול רבים, ניצחו וחזרו לבית המקדש.',
        'הם רצו להדליק את המנורה, אבל כל השמן היה טמא.',
        'חיפשו וחיפשו… ומצאו פך שמן קטן אחד, עם חותם הכהן הגדול.',
        'בפך היה שמן ליום אחד בלבד.',
        'הדליקו בכל זאת – והשמן המשיך לדלוק.',
        'יום, ועוד יום… שמונה ימים שלמים!',
        'נס גדול היה שם. חג חנוכה שמח מאופק את טל מנופים!'],
 'en': ['Over two thousand years ago, the Temple in Jerusalem was defiled.',
        'The Maccabees, few against many, won and returned to the Temple.',
        'They wanted to light the menorah, but all the oil was impure.',
        'They searched and searched… and found one small jar of pure oil.',
        'The jar held oil for just one day.',
        'They lit it anyway – and the oil kept burning.',
        'One day, and another… eight whole days!',
        'A great miracle happened there. Happy Hanukkah from Ofek et Tal Cranes!'],
 'ru': ['Более двух тысяч лет назад Храм в Иерусалиме был осквернён.',
        'Маккавеи, немногие против многих, победили и вернулись в Храм.',
        'Они хотели зажечь менору, но всё масло было нечистым.',
        'Искали и искали… и нашли один маленький кувшин чистого масла.',
        'Масла в нём хватало только на один день.',
        'Его всё равно зажгли – и масло продолжало гореть.',
        'День, ещё день… целых восемь дней!',
        'Великое чудо было там. Счастливой Хануки от Ofek et Tal Cranes!'],
 'fr': ["Il y a plus de deux mille ans, le Temple de Jérusalem fut profané.",
        'Les Maccabées, peu nombreux face à beaucoup, ont vaincu et sont revenus au Temple.',
        "Ils voulaient allumer la ménorah, mais toute l'huile était impure.",
        "Ils ont cherché… et trouvé une seule petite fiole d'huile pure.",
        "La fiole contenait de l'huile pour un seul jour.",
        "Ils l'ont allumée quand même – et l'huile a continué de brûler.",
        'Un jour, puis un autre… huit jours entiers !',
        "Un grand miracle a eu lieu là-bas. Joyeux Hanoukka de Ofek et Tal Cranes !"],
}


async def tts(text, voice, path):
    import edge_tts
    await edge_tts.Communicate(text, voice).save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]  # optional "3-he" filters
    for lang, lines in STORY.items():
        for n in range(1, 9):
            key = '%d-%s' % (n, lang)
            if only and key not in only: continue
            src = os.path.join(SRC, 'hanukkah-%s.mp4' % key)
            mp3 = os.path.join(OUT, 'v-%s.mp3' % key)
            if os.path.exists(os.path.join(OUT, 'hanukkah-%s.mp4' % key)): continue
            ok = False
            for v in [VOICE[lang], VOICE[lang], FALLBACK.get(lang, VOICE[lang])]:
                try:
                    asyncio.run(tts(lines[n - 1], v, mp3)); ok = True; break
                except Exception as e:
                    print('tts retry', key, v, e); import time; time.sleep(5)
            if not ok: print('SKIP', key); continue
            out = os.path.join(OUT, 'hanukkah-%s.mp4' % key)
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-i', mp3, '-filter_complex',
                            '[0:a]volume=0.35[m];[1:a]adelay=800|800,volume=1.6[v];[m][v]amix=inputs=2:duration=first:normalize=0[a]',
                            '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', out], check=True)
            os.remove(mp3)
            print(out)


if __name__ == '__main__':
    main()
