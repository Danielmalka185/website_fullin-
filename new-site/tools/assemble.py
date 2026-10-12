#!/usr/bin/env python3
"""Assemble index.html from index.src.html by inlining <!--#include name--> with _partials/name.html.
Also embeds content/copy.*.json into <script type="application/json" id="copy-LANG"> so the site works from file://.
Usage: python3 tools/assemble.py"""
import re, json, glob, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(root, 'index.src.html'), encoding='utf8').read()
def inc(m):
    p = os.path.join(root, '_partials', m.group(1) + '.html')
    if not os.path.exists(p):
        print('WARN missing partial', m.group(1), file=sys.stderr); return ''
    return open(p, encoding='utf8').read()
out = re.sub(r'<!--#include ([\w-]+)-->', inc, src)
blocks = []
for f in sorted(glob.glob(os.path.join(root, 'content', 'copy.*.json'))):
    lang = os.path.basename(f).split('.')[1]
    data = json.load(open(f, encoding='utf8'))
    blocks.append('<script type="application/json" id="copy-%s">%s</script>' % (lang, json.dumps(data, ensure_ascii=False).replace('</', '<\\/')))
out = out.replace('<!--#copy-->', '\n'.join(blocks))
open(os.path.join(root, 'index.html'), 'w', encoding='utf8').write(out)
print('index.html written', len(out) // 1024, 'KB')
