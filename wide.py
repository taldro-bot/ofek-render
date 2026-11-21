"""Make a regular 16:9 YouTube video from every Short: blurred-free layout = brand panel | short | contact panel, + 5s outro.
Source list: public Drive JSON written by the engine {id: {"v": mp4FileId, "j": jsonFileId}}. Output out/<id>w.mp4 + .json"""
import json, os, subprocess, sys, urllib.request
SRC = os.environ['WIDE_SRC']; MAXN = int(os.environ.get('MAXN', '8'))
def get(fid, path):
    req = urllib.request.Request('https://drive.google.com/uc?export=download&id=' + fid, headers={'User-Agent': 'Mozilla/5.0'})
    open(path, 'wb').write(urllib.request.urlopen(req, timeout=180).read())
src = json.loads(urllib.request.urlopen(urllib.request.Request('https://drive.google.com/uc?export=download&id=' + SRC, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read())
done = set(open('state/wide_done.txt').read().split()) if os.path.exists('state/wide_done.txt') else set()
todo = [k for k in sorted(src) if k not in done][:MAXN]
os.makedirs('out', exist_ok=True); made = []
for k in todo:
    try:
        get(src[k]['v'], '/tmp/in.mp4')
        title = k
        if src[k].get('j'):
            get(src[k]['j'], '/tmp/in.json'); j = json.load(open('/tmp/in.json')); title = j.get('title', k)
        else: j = {'id': k, 'title': k, 'lines': []}
        fc = ('[0:v][2:v]overlay=0:0[bg0];[1:v]scale=-2:1080,setsar=1[sv];[bg0][sv]overlay=656:0:shortest=1[a];'
              '[a][3:v]overlay=1264:0:shortest=1,format=yuv420p,fps=30[v0];'
              '[4:v]scale=1920:1080,setsar=1,format=yuv420p,fps=30[v1];'
              '[1:a]aresample=44100,aformat=channel_layouts=stereo[a0];[5:a]aresample=44100,aformat=channel_layouts=stereo[a1];'
              '[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][aa]')
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=0x0b0c0d:s=1920x1080:r=30', '-i', '/tmp/in.mp4',
               '-loop', '1', '-i', 'assets/wide/panel_left.png', '-loop', '1', '-i', 'assets/wide/panel_right.png',
               '-loop', '1', '-t', '5', '-i', 'assets/wide/outro.png', '-f', 'lavfi', '-t', '5', '-i', 'anullsrc=r=44100:cl=stereo',
               '-filter_complex', fc,
               '-map', '[v]', '-map', '[aa]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-c:a', 'aac', '-b:a', '128k',
               'out/%sw.mp4' % k]
        subprocess.run(cmd, check=True, timeout=600)
        j2 = dict(j); j2['id'] = k + 'w'; j2['title'] = title; j2['wide_of'] = k
        json.dump(j2, open('out/%sw.json' % k, 'w'), ensure_ascii=False)
        made.append(k)
    except Exception as e:
        print('FAIL', k, e, file=sys.stderr)
open('state/wide_done.txt', 'a').write(''.join(x + '\n' for x in todo))
print(' '.join(made))
