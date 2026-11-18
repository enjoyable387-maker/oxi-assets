"""Reflow the original OXI blog's vector artwork onto a 2:1 cover."""
from pathlib import Path
from html import escape
from copy import deepcopy
from functools import lru_cache
import json
import re
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
SOURCES = json.loads((HERE / 'brand/source-map.json').read_text())
ET.register_namespace('', 'http://www.w3.org/2000/svg')
K, R, W, P = '#0A0A0A', '#C93A22', '#FEFDFB', '#F1EEE8'
B = '#F7F6F3'
FONT = 'Apple SD Gothic Neo,Noto Sans CJK KR,sans-serif'

def tag(e): return e.tag.rsplit('}', 1)[-1]

@lru_cache(None)
def original(post_id):
    return ET.parse(HERE / 'brand/originals' / SOURCES[post_id]['file']).getroot() if post_id in SOURCES else None

def config(post):
    root = original(post['id'])
    if root is None:
        return {'style': 1, 'bg': B, 'theme': 'paper', 'index': int(post['id'][-3:])}
    counter = next((n.text for n in root if tag(n) == 'text' and re.fullmatch(r'\d+ / \d+', n.text or '')), '')
    index = int(counter.split('/')[0]) - 1 if counter else int(post['id'][-3:])
    return {'style': 1, 'bg': B, 'theme': 'paper', 'index': index}

def units(text):
    return sum(.33 if c.isspace() else .58 if ord(c) < 128 else 1 for c in text)

def text(x, y, value, size, fill, weight=800, spacing=-2):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" font-size="{size:.2f}" font-weight="{weight}" letter-spacing="{spacing}">{escape(value)}</text>'

MOTIFS = {'quote':'224469378114','menu':'224478204899','chart':'224469381079','calendar':'224469376738',
 'document':'224469369760','check':'224469379470','mobile':'224469379086','clock':'224469377734',
 'messages':'224469377165','link':'224469375433','form':'224469374999','photo':'224469374009',
 'files':'224469372506','type':'224469376172','layout':'224469373412','focus':'224469365247',
 'map':'224469365247','space':'224469365247','key':'224469374009','shop':'224469373412'}

def render(post, lines, kind, native_character):
    root = original(post['id']); ink = K; x = 24
    backdrop = f'<rect width="1200" height="600" fill="{B}"/>'
    backdrop += f'<circle cx="908" cy="300" r="282" fill="{P}"/>'

    label = post['category']
    if root is not None:
        original_headlines = [n.text for n in root if tag(n) == 'text' and float(n.get('font-size','0')) >= 45 and float(n.get('y','0')) < 500]
        if len(original_headlines) >= 2: lines = original_headlines[:2]
        label = next((n.text for n in root if tag(n) == 'text' and n.get('y') == '108'), label)
    size = min(96, 620 / max(units(s) for s in lines))
    pill_width = max(230, 44 + units(label) * 24)
    content = f'<rect x="{x}" y="16" width="{pill_width:.1f}" height="46" rx="23" fill="{R}"/>'
    content += f'<text x="{x + pill_width / 2:.1f}" y="39" text-anchor="middle" dominant-baseline="central" fill="{W}" font-family="{FONT}" font-size="24" font-weight="700" letter-spacing="0">{escape(label)}</text>'
    content += text(x, 230, lines[0], size, ink) + text(x, 346, lines[1], size, R)

    motif_root = root if root is not None else original(MOTIFS.get(kind, '224469369760'))
    if motif_root is not None:
        motif = next((n for n in motif_root if tag(n) == 'g' and 'scale' in n.get('transform','')), None)
        if motif is not None:
            motif = deepcopy(motif); motif.set('transform', 'translate(1090 8) scale(.3)')
            for child in motif.iter():
                for attr in ('fill', 'stroke'):
                    if child.get(attr) not in (None, 'none'): child.set(attr, R)
            content += ET.tostring(motif, encoding='unicode')

    # Fill the artwork height rather than adding a white strip above and below it.
    # The tighter native viewBox contains the complete poses, including their shadow.
    content += f'<svg x="640" y="0" width="550" height="600" viewBox="-160 -180 400 440">{native_character}</svg>'

    logo_root = root if root is not None else original('224469378114')
    logo = next((n for n in logo_root if tag(n) == 'g' and '912' in n.get('transform','')), None)
    if logo is not None:
        logo = deepcopy(logo); logo.set('transform',f'translate({x} 576)')
        for child in logo.iter():
            if tag(child) == 'text': child.set('fill',ink)
            if tag(child) == 'svg': child.set('fill',R)
        content += ET.tostring(logo,encoding='unicode')
    content += text(492,586,'OXI COLUMN',17,ink,700,1)

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600" role="img" aria-labelledby="title desc"><title id="title">{escape(post["title"])}</title><desc id="desc">아주 옅은 웜그레이 배경의 OXI 칼럼 표지. 알약 라벨의 문구를 가로와 세로 중앙에 배치했습니다.</desc>{backdrop}{content}</svg>'
    for identifier in set(re.findall(r'\bid="([^"]+)"',svg)):
        svg = svg.replace(f'id="{identifier}"',f'id="p{post["id"]}-{identifier}"').replace(f'url(#{identifier})',f'url(#p{post["id"]}-{identifier})')
    return svg.replace('aria-labelledby="title desc"',f'aria-labelledby="p{post["id"]}-title p{post["id"]}-desc"')
