"""Render Hebrew jobs whose Soniox dub is ready (engine writes a public Drive manifest). Prints ids rendered-ready."""
import json, os, sys, urllib.request
MAN = os.environ.get('DUB_MANIFEST', '')
done = set(open('state/dubbed.txt').read().split()) if os.path.exists('state/dubbed.txt') else set()
pend = [x for x in open('state/pending.txt').read().split() if x not in done] if os.path.exists('state/pending.txt') else []
if not MAN or not pend: sys.exit(0)
man = json.loads(urllib.request.urlopen(urllib.request.Request('https://drive.google.com/uc?export=download&id=' + MAN, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read() or b'{}')
for jid in pend[:int(os.environ.get('MAXN', '8'))]:
    if jid not in man: continue
    p = 'jobs/%s.json' % jid; j = json.load(open(p))
    j['audio_url'] = 'https://drive.google.com/uc?export=download&id=' + man[jid]['a']; j['dub_voice'] = man[jid]['v']
    json.dump(j, open(p, 'w'), ensure_ascii=False, indent=1)
    print(jid)
