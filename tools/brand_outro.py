"""28.11 Tal: brand any finished film – his bar (cartoon + name + phone + 'מנופאי אחד למיליון') on screen the whole time,
and his words spoken at the end in a male voice (edge-tts). python tools/brand_outro.py IN.mp4 OUT.mp4"""
import asyncio, subprocess, sys, json
import edge_tts
TXT = ('אופק את טל מנופים. חברה לעבודות גובה, שירותי מנוף, ומדריך לעבודה בגובה. '
       'טלפון: אֶפֶס חָמֵשׁ אֶפֶס, תֵּשַׁע אֶפֶס שְׁמוֹנֶה, אַחַת אַחַת אַחַת אַרְבַּע. '
       'לא כל יום מוצאים כזה מנופאי. מנופאי אחד למיליון!')
VOICE = 'he-IL-AvriNeural'
BAR = 'assets/outro/bar_he.png'


def dur(p):
    return float(json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', p]))['format']['duration'])


async def say(path):
    for v in (VOICE, VOICE, VOICE):   # never Hila – retries only
        try:
            await edge_tts.Communicate(TXT, v, rate='+4%').save(path); return
        except Exception as e:
            print('tts retry', e)
    raise SystemExit('tts failed')


def main(src, dst):
    asyncio.run(say('/tmp/outro.mp3'))
    D, O = dur(src), dur('/tmp/outro.mp3')
    start = max(0.0, D - 8.0)          # Tal's words start over the last 8 s (the end card), not after it
    ext = max(0.0, start + O + 0.8 - D)  # freeze the last frame only for what's left
    total = D + ext
    fc = ('[0:v]tpad=stop_mode=clone:stop_duration=%.2f,scale=1080:1920[v0];'
          '[2:v]format=rgba[b];[v0][b]overlay=0:H-h-110:enable=\'lt(t,%.2f)\'[v];'
          '[0:a]apad,atrim=0:%.2f,volume=0.55[a0];'
          '[1:a]adelay=%d|%d,apad,atrim=0:%.2f[a1];'
          '[a0][a1]amix=inputs=2:normalize=0[a]') % (ext, start, total, int(start * 1000) + 300, int(start * 1000) + 300, total)
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', src, '-i', '/tmp/outro.mp3', '-loop', '1', '-i', BAR,
                           '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-t', '%.2f' % total,
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', dst])
    print('done', dst, '%.1fs' % dur(dst))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
