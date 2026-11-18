// OXI 캐릭터 (확정 방향: A+B 합본 · 쌍눈) — 리소로 찍은 ◆
// 몸은 로고의 마름모(반대각선 100, 가운데가 원점). 빨강 판이 검정 판에서 (-7, 6) 어긋나 찍힌다.
//   oxiG(o)   → <g> 안에 넣을 조각 (장면 안에 translate/scale 로 배치)
//   oxiSVG(o) → 캐릭터만 담은 <svg> (viewBox -200 -190 400 470)
// 옵션: theme 'paper'|'dark'|'red'(버밀리언 배경 — 몸이 종이색으로 뒤집힌다) · simple true 면 작은 크기용(어긋남·망점·그림자 없음, 선 굵게)
//       bg 배경색 · tilt 기울기 · limbs false 면 몸과 눈만
//       eyes 'half'|'open'|'squint'|'closed'|'happy'|'wink' · look [dx,dy] 눈동자 방향
//       mouth 'smirk'|'flat'|'o'|'grin'|'none' · legs 'stand'|'walk'|'walkA'|'walkB'
//       tone false 면 망점 없음 · plate 'k' 면 검정 판만(빨강 판 없이)
//       armL 'down'|'up' · armR 'down'|'up'|'wave'|'point'|'sheet'|'lens' · shadow false
const OX = { INK: '#0A0A0A', PAPER: '#FEFDFB', RED: '#C93A22', BEIGE: '#F1EEE8', LINE: 8, EDGE: 4.5 };
const OX_DIAMOND = '0,-100 100,0 0,100 -100,0';
const OX_X = '-20 51.48 -20 0 -71.48 0 -133.38 61.9 -195.29 0 -246.77 0 -246.77 51.48 -184.86 113.39 -246.77 175.29 -246.77 226.77 -195.29 226.77 -133.38 164.87 -71.48 226.77 -20 226.77 -20 175.29 -81.9 113.39 -20 51.48';
const OX_I = '113.41 113.35 226.76 0 0 0 113.38 113.39 0 226.77 226.77 226.77 226.77 226.7 113.41 113.35';
let _ox = 0;

function oxiG(o = {}) {
  const n = ++_ox, dark = o.theme === 'dark';
  const red = o.theme === 'red', simple = !!o.simple;
  const K = dark ? OX.PAPER : OX.INK;                       // 검정 판 (어두운 배경에서는 흰 잉크)
  const P = o.bg || (dark ? OX.INK : red ? OX.RED : OX.BEIGE);   // 비워 둔 곳 = 배경색
  const R = red ? OX.BEIGE : OX.RED;                        // 색 판 (버밀리언 배경에서는 종이색)
  const blend = dark || red ? 'normal' : 'multiply';
  const LINE = simple ? 12 : OX.LINE, EDGE = simple ? 8 : OX.EDGE;
  const off = simple ? '0 0' : '-7 6';
  const limbs = o.limbs !== false;
  const limb = (d) => `<path d="${d}" fill="none" stroke="${K}" stroke-width="${LINE}" stroke-linecap="round" stroke-linejoin="round"/>`;
  const glove = (x, y) => `<circle cx="${x}" cy="${y}" r="16" fill="${P}" stroke="${K}" stroke-width="${EDGE}"/>`;
  const shoe = (x, y, flip) => `<g transform="translate(${x} ${y}) scale(${flip ? -1 : 1} 1)">
      <path d="M-20 16 C-22 -14 6 -16 12 2 L40 8 C50 10 52 20 44 22 L-20 22 Z" fill="${P}" stroke="${K}" stroke-width="${EDGE}" stroke-linejoin="round"/>
      <path d="M-24 25 H48" stroke="${K}" stroke-width="9" stroke-linecap="round"/></g>`;
  const shoeRed = (x, y, flip) => `<g transform="translate(${x} ${y}) scale(${flip ? -1 : 1} 1)"><path d="M-4 -4 C4 -8 10 -4 12 2 L26 5 L22 20 L-18 20 Z" fill="${R}"/></g>`;

  // 다리
  const LEGS = {
    stand: { d: ['M-28 70 C-40 118 -14 158 -30 204', 'M28 70 C44 118 18 160 38 204'], s: [[-34, 206, true], [42, 206, false]] },
    walk:  { d: ['M-28 70 C-52 108 -58 150 -80 194', 'M28 70 C52 110 36 158 60 200'], s: [[-86, 196, true], [64, 202, false]] },
    // 오른쪽으로 걷기 두 박자 — 번갈아 쓰면 걷는 것처럼 보인다 (신발 코가 둘 다 오른쪽)
    walkA: { d: ['M-28 70 C-34 112 -52 150 -72 192', 'M28 70 C40 112 60 150 74 198'], s: [[-68, 194, false], [78, 200, false]] },
    walkB: { d: ['M-28 70 C-20 120 -8 160 -6 204', 'M28 70 C64 96 68 134 36 158'], s: [[-2, 206, false], [40, 160, false]] },
  }[o.legs || 'stand'];

  // 눈: 흰자 + 눈동자 + 위에서 내려오는 눈꺼풀(lid = 덮는 비율)
  const [lx, ly] = o.look || [5, 8];
  const lidEye = (cx, lid, k) => `<clipPath id="ox${n}${k}"><ellipse cx="${cx}" cy="-8" rx="18" ry="23"/></clipPath>
      <ellipse cx="${cx}" cy="-8" rx="18" ry="23" fill="${OX.PAPER}"/>
      <circle cx="${cx + lx}" cy="${-8 + ly}" r="9" fill="${OX.INK}"/>
      <g clip-path="url(#ox${n}${k})"><rect x="${cx - 20}" y="-33" width="40" height="${46 * lid + 2}" fill="${OX.INK}"/></g>
      <ellipse cx="${cx}" cy="-8" rx="18" ry="23" fill="none" stroke="${OX.INK}" stroke-width="${EDGE}"/>`;
  const arc = (cx, up) => `<path d="M${cx - 16} ${up ? -2 : -10} Q${cx} ${up ? -22 : 8} ${cx + 16} ${up ? -2 : -10}" fill="none" stroke="${OX.INK}" stroke-width="6" stroke-linecap="round"/>`;
  const lid = { half: .44, open: .1, squint: .62 }[o.eyes || 'half'];
  let face;
  if (o.eyes === 'closed') face = arc(-27, false) + arc(27, false);
  else if (o.eyes === 'happy') face = arc(-27, true) + arc(27, true);
  else if (o.eyes === 'wink') face = lidEye(-27, .44, 'l') + arc(27, true);
  else face = lidEye(-27, lid, 'l') + lidEye(27, lid, 'r');
  const MOUTH = { smirk: 'M-10 36 Q6 46 18 32', flat: 'M-9 39 H13', grin: 'M-15 31 Q2 54 19 31', o: 'M2 32 a6 7 0 1 0 .1 0' }[o.mouth || 'smirk'];
  const mouth = o.mouth === 'none' ? '' : `<path d="${MOUTH}" fill="none" stroke="${OX.INK}" stroke-width="5" stroke-linecap="round"/>`;

  // 팔
  const armL = o.armL === 'up'
    ? limb('M-80 -20 C-126 -26 -136 -72 -124 -104') + glove(-124, -112)
    : limb('M-80 20 C-122 36 -128 84 -112 110') + glove(-110, 118);
  let armR, extra = '', extraRed = '';
  switch (o.armR || 'down') {
    case 'wave': armR = limb('M80 -20 C126 -26 136 -72 124 -104') + glove(124, -112) +
      `<path d="M112 -128 L108 -146 M126 -132 L130 -150 M138 -122 L152 -134" stroke="${K}" stroke-width="5" stroke-linecap="round"/>`; break;
    case 'up': armR = limb('M80 -20 C126 -26 136 -72 124 -104') + glove(124, -112); break;
    case 'point': armR = limb('M82 14 C112 22 136 10 160 2') + glove(166, 0); break;
    case 'sheet': armR = limb('M82 14 C108 30 122 26 134 14');
      extra = `<g transform="translate(128 -66) rotate(9)"><rect width="60" height="78" rx="3" fill="${P}" stroke="${K}" stroke-width="${EDGE}"/></g>`;
      extraRed = `<g transform="translate(128 -66) rotate(9)"><path d="M12 22H48M12 38H48M12 54H32" stroke="${red ? OX.INK : OX.RED}" stroke-width="6" stroke-linecap="round"/></g>`;
      extra += glove(136, 16); break;
    case 'lens': armR = limb('M82 14 C108 30 126 22 140 6');
      extra = `<path d="M150 -8 L162 -30" stroke="${K}" stroke-width="${LINE}" stroke-linecap="round"/>
               <circle cx="176" cy="-56" r="29" fill="${P}" fill-opacity=".55" stroke="${K}" stroke-width="6.5"/>` + glove(144, 6); break;
    default: armR = limb('M80 20 C122 36 128 84 112 110') + glove(110, 118);
  }

  const shadow = limbs && !simple && o.shadow !== false
    ? `<ellipse cx="6" cy="236" rx="118" ry="13" fill="url(#oxr${n})" style="mix-blend-mode:${blend}"/>` : '';
  return `<defs>
      <pattern id="oxd${n}" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="4.5" cy="4.5" r="2.7" fill="${OX.INK}"/></pattern>
      <pattern id="oxr${n}" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(60)"><circle cx="4" cy="4" r="2.4" fill="${red ? OX.INK : OX.RED}"/></pattern>
      <linearGradient id="oxf${n}" x1="0" y1="0" x2="1" y2="1"><stop offset=".45" stop-color="#000"/><stop offset=".95" stop-color="#fff"/></linearGradient>
      <mask id="oxm${n}"><polygon points="${OX_DIAMOND}" fill="url(#oxf${n})"/></mask>
    </defs>
    ${shadow}
    <g transform="rotate(${o.tilt ?? -5})">
      ${limbs ? LEGS.d.map(limb).join('') + LEGS.s.map(s => shoe(...s)).join('') + armL : ''}
      ${o.plate === 'k' ? '' : `<polygon points="${OX_DIAMOND}" fill="${P}"/>`}
      <g transform="translate(${off})" style="mix-blend-mode:${blend}${o.plate === 'k' ? ';display:none' : ''}">
        <polygon points="${OX_DIAMOND}" fill="${R}"/>${limbs ? LEGS.s.map(s => shoeRed(...s)).join('') : ''}
      </g>
      ${simple || o.tone === false ? '' : `<rect x="-100" y="-100" width="200" height="200" fill="url(#oxd${n})" mask="url(#oxm${n})" opacity=".85"/>`}
      <polygon points="${OX_DIAMOND}" fill="none" stroke="${K}" stroke-width="${EDGE}" stroke-linejoin="round"/>
      ${o.eyes === 'none' ? '' : face + mouth}
      ${limbs ? armR + extra : ''}
      ${extraRed ? `<g transform="translate(-4 3)" style="mix-blend-mode:${blend}">${extraRed}</g>` : ''}
    </g>`;
}

function oxiSVG(o = {}) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-200 -190 400 470">${oxiG(o)}</svg>`;
}

// 종이 입자 — 칸 전체를 덮는 별도 층
function oxiGrain(dark) {
  const n = ++_ox;
  return `<svg xmlns="http://www.w3.org/2000/svg" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;mix-blend-mode:${dark ? 'screen' : 'multiply'};opacity:${dark ? .16 : .3}">
    <filter id="oxg${n}"><feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="7"/>
      <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.6 1.05"/></filter>
    <rect width="100%" height="100%" filter="url(#oxg${n})" fill="${dark ? '#fff' : '#000'}"/></svg>`;
}

if (typeof module !== 'undefined') module.exports = { oxiG, oxiSVG, oxiGrain, OX, OX_X, OX_I, OX_DIAMOND };
