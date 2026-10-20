#!/usr/bin/env python3
"""Build a clean deployable folder ../dist from new-site.
Copies only the pages, css, js and the assets that are actually referenced; strips internal HTML comments
(CHECK WITH OWNERS / TODO). Keeps BRIEF.md, ASSET_CATALOG.md, tools/, _partials/, content/ and unused assets OUT of the deployment.
Usage: python3 tools/assemble.py && python3 tools/build_dist.py"""
import os, re, shutil, glob, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dist = os.path.join(os.path.dirname(root), 'dist')
if os.path.isdir(dist): shutil.rmtree(dist)
os.makedirs(dist)
pages = [p for p in glob.glob(os.path.join(root, '*.html')) if os.path.basename(p) != 'index.src.html']
text_files = list(pages) + glob.glob(os.path.join(root, 'css', '*.css')) + glob.glob(os.path.join(root, 'js', '*.js')) + glob.glob(os.path.join(root, 'content', 'copy.*.json'))
pat = re.compile(r'assets/[A-Za-z0-9_\-./]+\.(?:webp|png|jpg|jpeg|svg|mp4|webm|ico|gif|avif|woff2?|json)')
needed = set()
for f in text_files:
    for m in pat.findall(open(f, encoding='utf8', errors='ignore').read()):
        needed.add(m)
missing = [a for a in sorted(needed) if not os.path.exists(os.path.join(root, a))]
def copy(rel):
    src = os.path.join(root, rel); dst = os.path.join(dist, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(src, dst)
for a in sorted(needed):
    if a not in missing: copy(a)
cm = re.compile(r'<!--[^>]*?(CHECK WITH OWNERS|TODO)[\s\S]*?-->', re.I)
for p in pages:
    s = open(p, encoding='utf8').read(); s = cm.sub('', s)
    open(os.path.join(dist, os.path.basename(p)), 'w', encoding='utf8').write(s)
for d in ('css', 'js'):
    shutil.copytree(os.path.join(root, d), os.path.join(dist, d))
open(os.path.join(dist, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n')
size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(dist) for f in fs)
print('dist ->', dist, '| assets', len(needed) - len(missing), '| bytes', size // 1024, 'KB')
if missing: print('MISSING referenced assets (not copied):', missing)
