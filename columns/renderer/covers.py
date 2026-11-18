"""Reflow original OXI blog cover artwork; retain the established mascot style."""
from pathlib import Path
from html import escape
import hashlib
import re
import json
import subprocess
from brand_layout import config, render

HERE = Path(__file__).resolve().parent
OUT = HERE / 'assets' / 'covers'
VERSION = 'oxi-warmgray-centered-label-v5'

# These are short cover headlines, not changes to the linked articles' titles.
COPY = {
 '224478204899': ('메뉴 이름은', '고객의 말로', 'menu'),
 '224469381079': ('제작 결과와', '성과를 나누세요', 'chart'),
 '224469380728': ('오픈 후 30일,', '무엇을 점검할까', 'calendar'),
 '224469380378': ('홈페이지 수정,', '기록을 남기세요', 'document'),
 '224469379842': ('광고 문구부터', '도착 화면까지', 'link'),
 '224469379470': ('예쁘다는 말보다', '확인할 네 가지', 'check'),
 '224469379086': ('모바일 점검,', '내 폰으로 끝까지', 'mobile'),
 '224469378505': ('광고비와 제작비,', '따로 비교하세요', 'quote'),
 '224469378114': ('같은 견적,', '다른 제작 범위', 'quote'),
 '224469377734': ('셀프 제작 비용,', '시간도 계산하세요', 'clock'),
 '224469377165': ('수정 의견을', '한곳에 모으는 법', 'messages'),
 '224469376738': ('제작 일정은', '자료 확정일부터', 'calendar'),
 '224469376172': ('회사 소개 글,', '현장의 말로 시작', 'type'),
 '224469375433': ('광고 클릭 뒤,', '문의는 누가 받을까', 'link'),
 '224469374999': ('문의폼의 완성,', '어디까지일까요', 'form'),
 '224469374613': ('문의 버튼,', '끝까지 눌러보세요', 'mobile'),
 '224469374009': ('시공 사진 전달 전,', '사용 범위부터', 'photo'),
 '224469373412': ('포트폴리오,', '작업 성격부터 확인', 'layout'),
 '224469372506': ('시공 사진 정리,', '파일 이름부터', 'files'),
 '224469371773': ('제작을 연결하기 전,', '여섯 가지 질문', 'check'),
 '224469369760': ('견적을 받기 전,', '요청서 한 장부터', 'document'),
 '224469365247': ('첫 화면에는', '고객이 찾는 한 문장', 'focus'),
 '224462122045': ('수정이 이어져도', '디자인을 지키는 기준', 'layout'),
 '224462120824': ('제작을 맡기기 전,', '자료부터 모으세요', 'files'),
 '224462119403': ('시안을 받았다면', '폰으로 먼저 보세요', 'mobile'),
 '224462118040': ('1인 업체 소개,', '무엇을 먼저 쓸까', 'type'),
 '224462116558': ('고객 후기 공개 전,', '가려야 할 정보', 'messages'),
 '224462115004': ('주거와 상업 공간,', '첫 화면도 다르게', 'space'),
 '224462109065': ('공사비 안내,', '범위를 먼저 적으세요', 'quote'),
 '224453391339': ('조회수만으로', '문의를 알 수 있을까', 'chart'),
 '224453391199': ('서비스 지역,', '어디까지 적을까요', 'map'),
 '224453391010': ('새로운 시공 사례,', '누가 업데이트할까', 'photo'),
 '224453390840': ('도메인 만료일,', '누가 챙기고 있나요', 'calendar'),
 '224453390188': ('문의폼 항목,', '무엇을 받아야 할까', 'form'),
 '224453389320': ('제작 가격표,', '금액만 적으면 될까', 'quote'),
 '224453386634': ('건축사무소의 메뉴,', '무엇이 달라야 할까', 'space'),
 '224453234986': ('랜딩 한 장일까,', '홈페이지 여러 장일까', 'layout'),
 '224451975338': ('사진이 적어도', '첫 홈페이지를 시작', 'photo'),
 '224451123026': ('플레이스가 있어도', '홈페이지가 필요할까', 'search'),
 '224449851500': ('홈페이지 인수인계,', '아이디만 받으면 될까', 'key'),
 '224448662370': ('현장이 쉬는 동안,', '홈페이지를 준비하세요', 'check'),
 '224447396774': ('타월 브랜드 SAITA,', '상품 밖의 이야기', 'shop'),
 '224447396171': ('무료 폰트라면', '어디든 써도 될까', 'type'),
 '224446566914': ('홈페이지 속도 점수,', '왜 달라질까요', 'clock'),
 '224444449619': ('시공 사례 사진에', '어떤 설명을 붙일까', 'photo'),
 '224444449859': ('소재를 보여주는', '브랜드의 화면 구성', 'space'),
 '224444449226': ('제작사가 없어져도', '홈페이지는 내 것일까', 'key'),
 '224444448313': ('급한 고객은', '어디서 전화를 걸까', 'mobile'),
 '224443346554': ('견적 경쟁에서', '가격 밖의 기준 만들기', 'quote'),
 '224442200708': ('갤러리의 첫 화면,', '작품 목록을 뺀 이유', 'layout'),
}

def fallback(post):
    title = re.sub(r'^(인테리어\s+)?홈페이지\s*', '', post['title']).strip()
    words = title.split()
    lines = ['', '']
    for word in words:
        target = 0 if len(lines[0]) + len(word) < 13 else 1
        if len(lines[target]) + len(word) + 1 > 17:
            lines[target] = (lines[target] or word)[:15].rstrip(',.') + '…'
            break
        lines[target] += (' ' if lines[target] else '') + word
    if not lines[1]: lines[1] = '홈페이지 제작 이야기'
    kind = 'chart' if post['category'] == '운영·관리' else 'layout' if post['category'] == '홈페이지 설계' else 'document'
    return *lines, kind

def native_parts(posts):
    rows = [dict(id=p['id'], **config(p)) for p in posts]
    result = subprocess.run(['node', str(HERE / 'mascot-parts.cjs')], input=json.dumps(rows),
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def cover_svg(post, native_character=None):
    first, second, kind = COPY.get(post['id'], fallback(post))
    if native_character is None: native_character = native_parts([post])[post['id']]
    return render(post, [first, second], kind, native_character)


def build_covers(posts):
    OUT.mkdir(parents=True, exist_ok=True)
    posts = [p for p in posts if re.fullmatch(r'\d+', p['id'])]
    characters = native_parts(posts)
    result = []
    for post in posts:
        svg = cover_svg(post, characters[post['id']])
        path = OUT / (post['id'] + '.svg')
        if not path.exists() or path.read_text() != svg: path.write_text(svg)
        revision = hashlib.sha256((VERSION + svg).encode()).hexdigest()[:12]
        result.append(dict(post, image=f"/column-study/assets/covers/{post['id']}.svg?v={revision}", coverRatio='2:1'))
    return result
