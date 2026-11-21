#!/usr/bin/env python3
"""Download job photos given as URLs (e.g. public Drive links) and write <job>.local with local paths."""
import json, os, sys, urllib.request
job_path = sys.argv[1]
job = json.load(open(job_path, encoding='utf-8'))
d = os.path.join('tmp', 'photos', job['id']); os.makedirs(d, exist_ok=True)
local = []
for i, p in enumerate(job['photos']):
    if p.startswith('http'):
        out = os.path.join(d, '%02d.jpg' % i)
        req = urllib.request.Request(p, headers={'User-Agent': 'Mozilla/5.0'})
        open(out, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
        local.append(out)
    else:
        local.append(p)
job['photos'] = local
if job.get('audio_url'):
    a = os.path.join(d, 'voice.mp3')
    req = urllib.request.Request(job['audio_url'], headers={'User-Agent': 'Mozilla/5.0'})
    open(a, 'wb').write(urllib.request.urlopen(req, timeout=120).read())
    job['audio'] = a
json.dump(job, open(job_path + '.local', 'w', encoding='utf-8'), ensure_ascii=False)
print('photos', len(local))
