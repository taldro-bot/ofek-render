"""Render Hebrew jobs whose Soniox dub is ready (engine writes a public Drive manifest). Prints ids rendered-ready."""
import json, os, sys, urllib.request
MAN = os.environ.get('DUB_MANIFEST', '')
done = set(open('state/dubbed.txt').read().split()) if os.path.exists('state/dubbed.txt') else set()
pend = [x for x in open('state/pending.txt').read().split() if x not in done] if os.path.exists('state/pending.txt') else []
if not MAN or not pend: sys.exit(0)
man = json.loads(urllib.request.urlopen(urllib.request.Request('https://drive.google.com/uc?export=download&id=' + MAN, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read() or b'{}')
n = 0
for jid in pend:   # 21.11: take the first MAXN that are dubbed (not just the first MAXN in the list)
    if jid not in man or not os.path.exists('jobs/%s.json' % jid): continue
    if n >= int(os.environ.get('MAXN', '8')): break
    n += 1
    p = 'jobs/%s.json' % jid; j = json.load(open(p))
    j['audio_url'] = 'https://drive.google.com/uc?export=download&id=' + man[jid]['a']; j['dub_voice'] = man[jid]['v']
    if man[jid].get('a2'): j['answer_url'] = 'https://drive.google.com/uc?export=download&id=' + man[jid]['a2']
    elif j.get('quizvid'): n -= 1; continue   # quiz needs both voices
    json.dump(j, open(p, 'w'), ensure_ascii=False, indent=1)
    print(jid)
