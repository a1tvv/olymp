#!/usr/bin/env python3
"""Пересобирает README.md и картинки в assets/.

1. Прогоняет каждое решение на примерах из tests/ и ставит статус:
   «Решена» — все примеры прошли, «Черновик» — решение есть, но падает, «Скоро» — решения нет.
2. Считает статистику и рисует карточки в стиле iOS.

Запуск: python3 scripts/build.py  (то же самое делает git-хук при каждом коммите)
"""
import glob
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
REPO_URL = 'https://github.com/a1tvv'
TIME_LIMIT = 10  # секунд на один пример: с запасом, CI-машины бывают медленными

FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace"
GRAD = {
    'green': ('#4ade80', '#1e9e47'), 'orange': ('#ffb340', '#d26a00'), 'gray': ('#7c7c80', '#3a3a3c'),
    'blue': ('#64d2ff', '#0a84ff'), 'violet': ('#d48cff', '#7d3bd1'),
}
STATUS = {
    'done': dict(label='Решена', color='#30d158', grad='green', w=124),
    'draft': dict(label='Черновик', color='#ff9f0a', grad='orange', w=146),
    'soon': dict(label='Скоро', color='#98989d', grad='gray', w=108),
}
AI_STOPS = ('<stop offset="0" stop-color="#ff9f0a"/><stop offset="0.35" stop-color="#ff375f"/>'
            '<stop offset="0.7" stop-color="#bf5af2"/><stop offset="1" stop-color="#0a84ff"/>')
TILE = ('<linearGradient id="tile" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#161618"/><stop offset="1" stop-color="#000000"/></linearGradient>')
TITANIUM = ('<linearGradient id="titanium" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0.2" stop-color="#ffffff"/><stop offset="1" stop-color="#8e8e93"/></linearGradient>')


# ───────────────────────── проверка решений ─────────────────────────

def find_solution(cdir, letter):
    for ext in ('py', 'cpp'):
        path = os.path.join(cdir, 'solutions', f'{letter}.{ext}')
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            return path
    return None


def run(cmd, data):
    return subprocess.run(cmd, input=data, capture_output=True, text=True, timeout=TIME_LIMIT)


def judge(cdir, letter, workdir):
    solution = find_solution(cdir, letter)
    if not solution:
        return 'soon'
    if solution.endswith('.cpp'):
        compiler = shutil.which('g++') or shutil.which('clang++')
        exe = os.path.join(workdir, letter)
        if not compiler or subprocess.run([compiler, '-std=c++17', '-O2', solution, '-o', exe],
                                          capture_output=True).returncode:
            return 'draft'
        cmd = [exe]
    else:
        cmd = [sys.executable, solution]

    tests = sorted(glob.glob(os.path.join(cdir, 'tests', letter, '*.in')))
    checker = os.path.join(cdir, 'tests', letter, 'check.py')
    if not tests:
        return 'draft'
    for test in tests:
        with open(test) as f:
            data = f.read()
        try:
            result = run(cmd, data)
        except subprocess.TimeoutExpired:
            return 'draft'
        if result.returncode:
            return 'draft'
        if os.path.isfile(checker):
            ok = run([sys.executable, checker, test], result.stdout).returncode == 0
        else:
            with open(test[:-3] + '.out') as f:
                ok = result.stdout.split() == f.read().split()
        if not ok:
            return 'draft'
    return 'done'


def load():
    contests = []
    with tempfile.TemporaryDirectory() as workdir:
        for path in sorted(glob.glob(os.path.join(ROOT, 'contests', '*', 'contest.json')), reverse=True):
            cdir = os.path.dirname(path)
            with open(path) as f:
                contest = json.load(f)
            contest['slug'] = os.path.basename(cdir)
            for p in contest['problems']:
                p['status'] = judge(cdir, p['letter'], workdir)
                p['solution'] = find_solution(cdir, p['letter'])
            contests.append(contest)
    with open(os.path.join(ROOT, 'algorithms', 'algorithms.json')) as f:
        algorithms = json.load(f)
    return contests, algorithms


# ───────────────────────── SVG-помощники ─────────────────────────

def esc(s):
    return html.escape(str(s), quote=False)


def grad_def(gid, name):
    a, b = GRAD[name]
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')


def write_svg(path, w, h, label, defs, body):
    full = os.path.join(ASSETS, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                f'role="img" aria-label="{html.escape(label)}">\n<defs>{defs}</defs>\n'
                f'<g font-family="{FONT}">\n{body}\n</g>\n</svg>\n')


def app_icon(x, y, size, gid, inner):
    r = size * 0.26
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{r}" fill="url(#{gid})"/>'
            f'<rect x="{x + .5}" y="{y + .5}" width="{size - 1}" height="{size - 1}" rx="{r}" fill="none" '
            f'stroke="#ffffff" stroke-opacity="0.18"/>' + inner)


def icon_text(x, y, size, text, fs):
    return (f'<text x="{x + size / 2}" y="{y + size / 2 + fs * 0.36}" font-size="{fs}" font-weight="700" '
            f'fill="#ffffff" text-anchor="middle">{esc(text)}</text>')


def rich(x, y, line, fs=21):
    """Строка, где `текст в обратных кавычках` выделяется моноширинным голубым."""
    out = f'<text x="{x}" y="{y}" font-size="{fs}" font-weight="500" fill="#d1d1d6">'
    for i, part in enumerate(line.split('`')):
        if not part:
            continue
        if i % 2:
            out += (f'<tspan font-family="{MONO}" font-size="{fs - 2}" font-weight="600" '
                    f'fill="#64d2ff">{esc(part)}</tspan>')
        else:
            out += f'<tspan>{esc(part)}</tspan>'
    return out + '</text>'


CARD_ROW = '<rect x="0.5" y="6.5" width="{w}" height="119" rx="26" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'


# ───────────────────────── карточки ─────────────────────────

def banner(total):
    island = (
        '<rect x="530" y="30" width="140" height="46" rx="23" fill="#000000" stroke="#ffffff" stroke-opacity="0.16">'
        '<animate attributeName="width" values="140;140;480;480;140" keyTimes="0;0.1;0.2;0.86;1" dur="7s" '
        'repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;0.3 0.9 0.2 1;0 0 1 1;0.5 0 0.2 1"/>'
        '<animate attributeName="x" values="530;530;360;360;530" keyTimes="0;0.1;0.2;0.86;1" dur="7s" '
        'repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;0.3 0.9 0.2 1;0 0 1 1;0.5 0 0.2 1"/></rect>'
        '<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.18;0.24;0.82;0.86;1" '
        'dur="7s" repeatCount="indefinite"/>'
        '<circle cx="393" cy="53" r="12" fill="#30d158"/>'
        '<path d="M387 53.5l4 4 7.5-8" fill="none" stroke="#000000" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'
        '<text x="416" y="59.5" font-size="18" font-weight="600" fill="#ffffff">Accepted</text>'
        f'<text x="816" y="59.5" font-size="18" font-weight="600" fill="#30d158" text-anchor="end">решено {total}</text></g>'
    )
    defs = (f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="1">{AI_STOPS}'
            '<animateTransform attributeName="gradientTransform" type="rotate" from="0 0.5 0.5" to="360 0.5 0.5" '
            'dur="9s" repeatCount="indefinite"/></linearGradient>'
            f'<linearGradient id="aiText" x1="0" y1="0" x2="1" y2="0">{AI_STOPS}</linearGradient>' + TITANIUM +
            '<radialGradient id="spot" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffffff" stop-opacity="0.07"/>'
            '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>'
            '<filter id="edgeGlow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="20"/></filter>'
            '<clipPath id="card"><rect width="1200" height="600" rx="32"/></clipPath>')
    body = (
        '<g clip-path="url(#card)"><rect width="1200" height="600" fill="#000000"/>'
        '<ellipse cx="600" cy="320" rx="560" ry="260" fill="url(#spot)"/>'
        '<rect width="1200" height="600" rx="32" fill="none" stroke="url(#ai)" stroke-width="40" filter="url(#edgeGlow)" opacity="0.85"/>'
        '<rect x="1.5" y="1.5" width="1197" height="597" rx="30.5" fill="none" stroke="url(#ai)" stroke-width="3"/></g>'
        + island +
        '<text x="600" y="206" text-anchor="middle" font-size="28" font-weight="600" fill="url(#aiText)">Олимпиадное программирование</text>'
        '<text x="600" y="318" text-anchor="middle" font-size="104" font-weight="700" letter-spacing="-3" fill="url(#titanium)">Алтай Абдурахим</text>'
        '<text x="600" y="392" text-anchor="middle" font-size="36" font-weight="600" fill="#86868b">Алгоритмы. Контесты. Разборы.</text>'
        '<text x="600" y="466" text-anchor="middle" font-size="26" font-weight="500" fill="#2997ff">Смотреть решения ›</text>'
    )
    write_svg('banner.svg', 1200, 600, 'Алтай Абдурахим — олимпиадное программирование', defs, body)


def stats(total, from_contests, from_algorithms, contests, soon):
    latest = contests[0] if contests else None
    # отсчёт до итоговой цифры: последние 4 значения, без анимации видна сразу итоговая
    frames = list(range(max(1, total - 3), total + 1)) if total else [0]
    size = {1: 360, 2: 300}.get(len(str(total)), 220)
    step = 0.8 / len(frames)
    numbers = ''
    for i, n in enumerate(frames[:-1]):
        a, b = i * step / 0.8, (i + 1) * step / 0.8
        numbers += (f'<text x="30" y="420" opacity="0">{n}<animate attributeName="opacity" values="0;1;0" '
                    f'keyTimes="0;{a:.3f};{min(b, 0.999):.3f}" calcMode="discrete" dur="0.8s" fill="freeze"/></text>')
    numbers += (f'<text x="30" y="420">{frames[-1]}<animate attributeName="opacity" values="0;1" '
                f'keyTimes="0;{(len(frames) - 1) * step / 0.8 if len(frames) > 1 else 0.001:.3f}" '
                f'calcMode="discrete" dur="0.8s" fill="freeze"/></text>')

    keys = soon[:3] if len(soon) <= 3 else soon[:2] + [f'+{len(soon) - 2}']
    soon_body = '<text x="951" y="344" font-size="24" fill="#ff9f0a">Скоро</text>'
    if keys:
        for i, k in enumerate(keys):
            x = 951 + 72 * i
            soon_body += (f'<rect x="{x}" y="378" width="60" height="60" rx="16" fill="#1c1c1e" stroke="#ffffff" stroke-opacity="0.12"/>'
                          f'<text x="{x + 30}" y="419" font-size="{30 if len(k) == 1 else 22}" font-weight="700" '
                          f'fill="#f5f5f7" text-anchor="middle">{esc(k)}</text>')
        soon_body += '<text x="951" y="490" font-size="22" fill="#86868b">в работе</text>'
    else:
        soon_body = ('<text x="951" y="344" font-size="24" fill="#30d158">Готово</text>'
                     '<text x="951" y="440" font-size="58" font-weight="700" fill="#30d158">✓</text>'
                     '<text x="951" y="490" font-size="22" fill="#86868b">всё решено</text>')

    contest_name = (f'<text x="1152" y="170" font-size="32" font-weight="700" fill="#f5f5f7" text-anchor="end">{esc(latest["series"])}</text>'
                    f'<text x="1152" y="208" font-size="22" fill="#86868b" text-anchor="end">{esc(latest["title"])} · {latest["year"]}</text>'
                    if latest else '')
    defs = (f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="1">{AI_STOPS}</linearGradient>'
            '<linearGradient id="blue" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#64d2ff"/><stop offset="1" stop-color="#0a84ff"/></linearGradient>'
            + TITANIUM + TILE +
            '<filter id="blur" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="60"/></filter>'
            '<clipPath id="t1"><rect width="590" height="540" rx="32"/></clipPath>')
    body = (
        '<g font-weight="600">'
        '<g clip-path="url(#t1)"><rect width="590" height="540" fill="url(#tile)"/>'
        '<circle cx="470" cy="470" r="150" fill="url(#ai)" opacity="0.35" filter="url(#blur)"/></g>'
        '<rect x="0.5" y="0.5" width="589" height="539" rx="31.5" fill="none" stroke="#ffffff" stroke-opacity="0.1"/>'
        '<text x="48" y="86" font-size="24" fill="#86868b">Решено задач</text>'
        f'<g font-size="{size}" font-weight="700" letter-spacing="-10" fill="url(#ai)">{numbers}</g>'
        f'<text x="48" y="490" font-size="22" fill="#86868b">{from_contests} — контесты  ·  {from_algorithms} — алгоритмы</text>'
        '<rect x="610.5" y="0.5" width="589" height="259" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        '<text x="658" y="86" font-size="24" fill="#86868b">Контесты</text>'
        f'<text x="650" y="218" font-size="150" font-weight="700" letter-spacing="-4" fill="url(#blue)">{len(contests)}</text>'
        + contest_name +
        '<rect x="610.5" y="280.5" width="284" height="259" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        '<text x="646" y="344" font-size="24" fill="#86868b">Языки</text>'
        '<text x="644" y="440" font-size="58" font-weight="700" letter-spacing="-1" fill="url(#titanium)">C++17</text>'
        '<text x="646" y="490" font-size="32" fill="#86868b">Python 3</text>'
        '<rect x="915.5" y="280.5" width="284" height="259" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        + soon_body + '</g>'
    )
    label = f'Решено задач: {total} ({from_contests} с контестов, {from_algorithms} из алгоритмов). Контестов: {len(contests)}.'
    if soon:
        label += ' Скоро: ' + ', '.join(soon) + '.'
    write_svg('stats.svg', 1200, 540, label, defs, body)


def contest_card(c):
    probs = c['problems']
    n, gap = len(probs), 16
    w = (1104 - gap * (n - 1)) / n
    label_fs = 20 if w >= 150 else 16
    chips = ''
    for i, p in enumerate(probs):
        st = STATUS[p['status']]
        x = 48 + i * (w + gap)
        done = p['status'] != 'soon'
        fill = st['color'] if done else '#ffffff'
        letter_color = '#f5f5f7' if done else '#98989d'
        dot = (f'<circle cx="{x + w - 28}" cy="224" r="9" fill="{st["color"]}"/>' if done else
               f'<circle cx="{x + w - 28}" cy="224" r="9" fill="none" stroke="#98989d" stroke-width="2"/>')
        appear = (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{i / (i + 5):.2f};1" '
                  f'dur="{0.5 + 0.1 * i:.1f}s" fill="freeze"/>')
        chips += (f'<g>{appear}<rect x="{x:.1f}" y="196" width="{w:.1f}" height="126" rx="24" fill="{fill}" '
                  f'fill-opacity="{0.1 if done else 0.04}" stroke="{fill}" stroke-opacity="{0.45 if done else 0.12}"/>'
                  f'<text x="{x + 28:.1f}" y="262" font-size="44" font-weight="700" fill="{letter_color}">{p["letter"]}</text>{dot}'
                  f'<text x="{x + 28:.1f}" y="300" font-size="{label_fs}" fill="{st["color"]}">{st["label"]}</text></g>')
    defs = TILE + TITANIUM + f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="0">{AI_STOPS}</linearGradient>'
    body = (
        '<rect x="0.5" y="0.5" width="1199" height="369" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        f'<g font-weight="600"><text x="48" y="84" font-size="22" fill="url(#ai)">{esc(c["series"])} · {esc(c["date"])}</text>'
        f'<text x="46" y="146" font-size="54" font-weight="700" letter-spacing="-1.5" fill="url(#titanium)">{esc(c["title"])}</text>'
        f'{chips}</g>'
    )
    summary = '; '.join(f'{p["letter"]} — {STATUS[p["status"]]["label"].lower()}' for p in probs)
    write_svg(f'contests/{c["slug"]}/card.svg', 1200, 370, f'{c["series"]} {c["title"]}, {c["date"]}: {summary}', defs, body)


def problem_row(c, p):
    st = STATUS[p['status']]
    px = 912 - st['w']
    body = (CARD_ROW.format(w=935) + app_icon(22, 24, 84, 'ic', icon_text(22, 24, 84, p['letter'], 42)) +
            f'<text x="128" y="61" font-size="30" font-weight="600" fill="#f5f5f7">{esc(p["name"])}</text>'
            f'<text x="128" y="99" font-size="21" font-weight="500" fill="#86868b">{esc(" · ".join(p["topics"]))}</text>'
            f'<rect x="{px}" y="30" width="{st["w"]}" height="36" rx="18" fill="{st["color"]}" fill-opacity="0.16"/>'
            f'<circle cx="{px + 20}" cy="48" r="5" fill="{st["color"]}"/>'
            f'<text x="{px + 34}" y="54.5" font-size="18" font-weight="600" fill="{st["color"]}">{st["label"]}</text>'
            '<text x="912" y="99" font-size="20" font-weight="500" fill="#2997ff" text-anchor="end">Условие ›</text>')
    write_svg(f'contests/{c["slug"]}/{p["letter"]}.svg', 948, 132, f'{p["letter"]} · {p["name"]} — {st["label"]}',
              TILE + grad_def('ic', st['grad']), body)


def button(name, label, caption, active):
    pill = '#0a84ff' if active else '#ffffff'
    body = ('<rect x="8.5" y="6.5" width="223" height="119" rx="26" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
            f'<rect x="40" y="32" width="160" height="46" rx="23" fill="{pill}" fill-opacity="{1 if active else 0.08}"/>'
            f'<text x="120" y="62" font-size="21" font-weight="600" fill="{"#ffffff" if active else "#98989d"}" text-anchor="middle">{label}</text>'
            f'<text x="120" y="105" font-size="18" font-weight="500" fill="#86868b" text-anchor="middle">{caption}</text>')
    write_svg(f'rows/{name}.svg', 240, 132, f'{label} · {caption}', TILE, body)


def editorials(c):
    items = [p for p in c['problems'] if p.get('editorial')]
    if not items:
        return False
    tw, th, gap = 590, 330, 20
    rows = (len(items) + 1) // 2
    defs = TILE + ''.join(grad_def(f'g{k}', v['grad']) for k, v in STATUS.items())
    body = ''
    for i, p in enumerate(items):
        tx, ty = (i % 2) * (tw + gap), (i // 2) * (th + gap)
        st = STATUS[p['status']]
        sub, sub_color = (st['label'].lower(), st['color']) if p['status'] != 'done' else (p.get('complexity', ''), '#86868b')
        body += (f'<rect x="{tx + .5}" y="{ty + .5}" width="{tw - 1}" height="{th - 1}" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
                 + app_icon(tx + 32, ty + 32, 64, f'g{p["status"]}', icon_text(tx + 32, ty + 32, 64, p['letter'], 32)) +
                 f'<text x="{tx + 116}" y="{ty + 60}" font-size="26" font-weight="600" fill="#f5f5f7">{esc(p["name"])}</text>'
                 f'<text x="{tx + 116}" y="{ty + 90}" font-family="{MONO}" font-size="18" font-weight="600" fill="{sub_color}">{esc(sub)}</text>')
        for j, line in enumerate(p['editorial'][:5]):
            y = ty + 146 + j * 38
            if not line.startswith('  '):
                body += f'<circle cx="{tx + 40}" cy="{y - 7}" r="4" fill="{st["color"]}"/>'
            body += rich(tx + 58, y, line.strip())
    write_svg(f'contests/{c["slug"]}/editorials.svg', 1200, rows * th + (rows - 1) * gap,
              'Разборы: ' + ', '.join(p['letter'] for p in items), defs, body)
    return True


def algorithm_row(a):
    name = os.path.splitext(os.path.basename(a['file']))[0]
    bars = ''.join(f'<rect x="{39 + i * 14}" y="{90 - h}" width="9" height="{h}" rx="3" fill="#ffffff"/>'
                   for i, h in enumerate((16, 28, 40, 52)))
    pill = a['complexity']
    w = 30 + 12 * len(pill)
    lang = 'C++' if a['file'].endswith('.cpp') else 'Python'
    body = (CARD_ROW.format(w=1199) + app_icon(22, 24, 84, 'ic', bars) +
            f'<text x="128" y="61" font-size="30" font-weight="600" fill="#f5f5f7">{esc(a["name"])}</text>'
            f'<text x="128" y="99" font-size="21" font-weight="500" fill="#86868b">{esc(a["about"])} · {lang}</text>'
            f'<rect x="{1128 - w}" y="48" width="{w}" height="36" rx="18" fill="#ffffff" fill-opacity="0.08"/>'
            f'<text x="{1128 - w / 2}" y="72" font-family="{MONO}" font-size="19" font-weight="600" fill="#f5f5f7" text-anchor="middle">{esc(pill)}</text>'
            '<path d="M1160 53l12 13-12 13" fill="none" stroke="#636366" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
    write_svg(f'rows/{name}.svg', 1200, 132, f'{a["name"]} — {pill}, {lang}', TILE + grad_def('ic', 'violet'), body)
    return name


def title(name, heading, subs):
    defs = f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="0">{AI_STOPS}</linearGradient>'
    body = f'<text x="2" y="62" font-size="54" font-weight="700" letter-spacing="-1.2" fill="url(#ai)">{esc(heading)}</text>'
    for i, sub in enumerate(subs):
        body += f'<text x="3" y="{104 + 34 * i}" font-size="25" font-weight="500" fill="#8e8e93">{esc(sub)}</text>'
    write_svg(f'titles/{name}.svg', 1200, 92 + 34 * len(subs), heading, defs, body)


def structure(contests):
    tree = [(0, 'olymp/', '')]
    tree.append((1, 'contests/', ''))
    for c in contests:
        tree += [(2, c['slug'] + '/', ''), (3, 'statements/', 'условия задач (PDF)'),
                 (3, 'solutions/', 'решения: A.py, B.py, …'), (3, 'tests/', 'примеры из условий'),
                 (3, 'contest.json', 'названия, темы, разборы')]
    tree += [(1, 'algorithms/', 'классические алгоритмы'), (1, 'scripts/', 'сборка README и проверка решений'),
             (1, 'assets/', 'картинки для README')]
    row, top, x0, ind = 46, 74, 48, 44
    h = top + row * len(tree) + 130
    defs = TILE + grad_def('folder', 'blue') + grad_def('root', 'violet') + grad_def('file', 'gray')
    lines, items = '', ''
    for i, (d, name, desc) in enumerate(tree):
        y, x = top + i * row, x0 + d * ind
        if d:
            p = max(k for k in range(i) if tree[k][0] == d - 1)
            px, py = x0 + (d - 1) * ind + 15, top + p * row
            lines += f'<path d="M{px} {py + 8}V{y - 8}H{x - 8}" fill="none" stroke="#3a3a3c" stroke-width="2"/>'
        if name.endswith('/'):
            fill = 'root' if d == 0 else 'folder'
            items += (f'<path transform="translate({x} {y - 19})" d="M0 4a3 3 0 0 1 3-3h7.5l3 3.5H27a3 3 0 0 1 3 3V19a3 3 0 0 1-3 3H3a3 3 0 0 1-3-3z" '
                      f'fill="url(#{fill})"/>')
        else:
            items += f'<path transform="translate({x + 5} {y - 22})" d="M0 3a3 3 0 0 1 3-3h10l7 7v15a3 3 0 0 1-3 3H3a3 3 0 0 1-3-3z" fill="url(#file)"/>'
        items += f'<text x="{x + 42}" y="{y}" font-family="{MONO}" font-size="21" font-weight="600" fill="#f5f5f7">{esc(name)}</text>'
        if desc:
            items += f'<text x="660" y="{y}" font-size="21" font-weight="500" fill="#86868b">{esc(desc)}</text>'
    ny = h - 78
    body = (f'<rect x="0.5" y="0.5" width="1199" height="{h - 1}" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
            + lines + items +
            f'<line x1="48" y1="{ny - 42}" x2="1152" y2="{ny - 42}" stroke="#ffffff" stroke-opacity="0.08"/>'
            + rich(48, ny, 'Новый контест — новая папка `contests/<год>-<название>/` с такой же структурой', fs=20)
            + rich(48, ny + 36, 'Статистика считается сама: при коммите решения прогоняются на `tests/`', fs=20))
    write_svg('structure.svg', 1200, h, 'Структура репозитория', defs, body)


def terminal():
    p, t, op, s, com, out = '#30d158', '#f5f5f7', '#ff375f', '#ffd60a', '#636366', '#64d2ff'
    lines = [
        [('# Python', com)],
        [('$ ', p), ('python3 contests/2026-icpc-qual/solutions/D.py ', t), ('<<<', op), (' 34', t)],
        [('8 15', out)], [],
        [('# C++', com)],
        [('$ ', p), ('clang++ -std=c++17 -O2 algorithms/sorting/bubble_sort_swaps.cpp -o bubble', t)],
        [('$ ', p), ('echo ', t), ('"4  4 2 3 1"', s), (' | ', op), ('./bubble', t)],
        [('5', out)], [],
        [('# Пересобрать README вручную', com)],
        [('$ ', p), ('python3 scripts/build.py', t)],
    ]
    lh, top = 36, 122
    h = top + lh * (len(lines) - 1) + 56
    body = (f'<rect x="0.5" y="0.5" width="1199" height="{h - 1}" rx="23.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
            '<rect x="1" y="1" width="1198" height="59" rx="23" fill="#ffffff" fill-opacity="0.04"/>'
            '<line x1="1" y1="60.5" x2="1199" y2="60.5" stroke="#ffffff" stroke-opacity="0.08"/>'
            + ''.join(f'<circle cx="{34 + 24 * k}" cy="30" r="7" fill="{col}"/>' for k, col in enumerate(('#ff5f57', '#febc2e', '#28c840')))
            + f'<text x="600" y="36" font-family="{MONO}" font-size="16" fill="#8e8e93" text-anchor="middle">zsh — olymp</text>')
    for i, segs in enumerate(lines):
        if segs:
            body += (f'<text x="48" y="{top + i * lh}" font-family="{MONO}" font-size="20" xml:space="preserve" style="white-space:pre">'
                     + ''.join(f'<tspan fill="{col}">{esc(txt)}</tspan>' for txt, col in segs) + '</text>')
    write_svg('run.svg', 1200, h, 'Запуск решений в терминале', TILE, body)


def footer():
    defs = (TITANIUM + f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="0">{AI_STOPS}'
            '<animateTransform attributeName="gradientTransform" type="translate" values="-0.3 0;0.3 0;-0.3 0" dur="8s" repeatCount="indefinite"/>'
            '</linearGradient><radialGradient id="spot" cx="0.5" cy="1" r="0.7"><stop offset="0" stop-color="#bf5af2" stop-opacity="0.22"/>'
            '<stop offset="1" stop-color="#bf5af2" stop-opacity="0"/></radialGradient>'
            '<clipPath id="card"><rect width="1200" height="380" rx="32"/></clipPath>')
    body = ('<g clip-path="url(#card)"><rect width="1200" height="380" fill="#000000"/><rect width="1200" height="380" fill="url(#spot)"/></g>'
            '<rect x="0.5" y="0.5" width="1199" height="379" rx="31.5" fill="none" stroke="#ffffff" stroke-opacity="0.1"/>'
            '<g font-weight="700" text-anchor="middle">'
            '<text x="600" y="160" font-size="96" letter-spacing="-3" fill="url(#titanium)">Stay hungry.</text>'
            '<text x="600" y="262" font-size="96" letter-spacing="-3" fill="url(#ai)">Stay foolish.</text>'
            '<text x="600" y="326" font-size="22" font-weight="600" fill="#86868b">Steve Jobs · 1955–2011</text></g>')
    write_svg('footer.svg', 1200, 380, 'Stay hungry. Stay foolish. — Steve Jobs, 1955–2011', defs, body)


# ───────────────────────── README ─────────────────────────

def section_title(anchor, name, alt):
    return f'<a name="{anchor}"></a>\n<img src="assets/titles/{name}.svg" alt="{alt}" width="100%">\n'


def readme(contests, algorithms, algo_rows, total, has_editorials):
    out = [
        '<!-- Этот файл собирается автоматически: python3 scripts/build.py. Правки вручную перезапишутся. -->',
        '<a href="#contests"><img src="assets/banner.svg" alt="Алтай Абдурахим — олимпиадное программирование" width="100%"></a>',
        '',
        '<p align="center">\n  <a href="#contests">Контесты&nbsp;›</a>&emsp;\n  <a href="#editorials">Разборы&nbsp;›</a>&emsp;\n'
        '  <a href="#algorithms">Алгоритмы&nbsp;›</a>&emsp;\n  <a href="#structure">Структура&nbsp;›</a>&emsp;\n'
        '  <a href="#run">Запуск&nbsp;›</a>\n</p>',
        '', '<br>', '',
        f'<img src="assets/stats.svg" alt="Решено задач: {total}" width="100%">',
        '', '<br>\n<br>', '',
        '<p align="center">\n  <i>«Talk is cheap. Show me the code.»</i><br>\n  <sub>— Linus Torvalds</sub>\n</p>',
        '', '<br>', '',
        section_title('contests', 'contests', 'Контесты'),
    ]
    for c in contests:
        base = f'contests/{c["slug"]}'
        out.append(f'<a href="{base}/statements"><img src="assets/contests/{c["slug"]}/card.svg" '
                   f'alt="{esc(c["series"])} {esc(c["title"])}, {esc(c["date"])}" width="100%"></a>\n')
        rows = []
        for p in c['problems']:
            L = p['letter']
            if p['solution']:
                code = os.path.relpath(p['solution'], ROOT)
                btn = 'btn-cpp' if code.endswith('.cpp') else 'btn-python'
                btn_alt = f'Код {L}'
            else:
                code, btn, btn_alt = f'{base}/statements/{L}.pdf', 'btn-soon', 'Скоро'
            rows.append(f'<a href="{base}/statements/{L}.pdf"><img src="assets/contests/{c["slug"]}/{L}.svg" '
                        f'alt="{L} · {esc(p["name"])} — {STATUS[p["status"]]["label"]}" width="79%"></a>'
                        f'<a href="{code}"><img src="assets/rows/{btn}.svg" alt="{btn_alt}" width="20%"></a><br>')
        out.append('<p>\n' + '\n'.join(rows) + '\n</p>\n\n<br>\n')
    if has_editorials:
        out.append(section_title('editorials', 'editorials', 'Разборы'))
        for c in contests:
            if any(p.get('editorial') for p in c['problems']):
                alt = ' '.join(f'{p["letter"]}: ' + '; '.join(l.strip().replace('`', '') for l in p['editorial'])
                               for p in c['problems'] if p.get('editorial'))
                out.append(f'<img src="assets/contests/{c["slug"]}/editorials.svg" alt="{esc(alt)}" width="100%">\n')
        out.append('<br>\n<br>\n')
    out.append(section_title('algorithms', 'algorithms', 'Алгоритмы'))
    for a, name in zip(algorithms, algo_rows):
        out.append(f'<a href="algorithms/{a["file"]}"><img src="assets/rows/{name}.svg" '
                   f'alt="{esc(a["name"])} — {esc(a["complexity"])}" width="100%"></a>')
    out += ['', '<br>\n<br>', '',
            section_title('structure', 'structure', 'Структура'),
            '<img src="assets/structure.svg" alt="Структура репозитория" width="100%">',
            '', '<br>\n<br>', '',
            section_title('run', 'run', 'Запуск'),
            '<img src="assets/run.svg" alt="Запуск решений в терминале" width="100%">',
            '',
            '<details>\n<summary>Скопировать команды</summary>\n<br>\n\n```bash\n# Python\n'
            'python3 contests/2026-icpc-qual/solutions/D.py <<< 34\n# 8 15\n\n# C++\n'
            'clang++ -std=c++17 -O2 algorithms/sorting/bubble_sort_swaps.cpp -o bubble\necho "4  4 2 3 1" | ./bubble\n# 5\n\n'
            '# Пересобрать README вручную\npython3 scripts/build.py\n```\n\n</details>',
            '', '<br>', '',
            '<img src="assets/footer.svg" alt="Stay hungry. Stay foolish. — Steve Jobs, 1955–2011" width="100%">',
            '',
            '<p align="center">\n  <sub>Сделано с ☕ и <code>-O2</code> &nbsp;·&nbsp; '
            f'<a href="{REPO_URL}">@a1tvv</a></sub>\n</p>', '']
    with open(os.path.join(ROOT, 'README.md'), 'w') as f:
        f.write('\n'.join(out))


def main():
    contests, algorithms = load()
    for sub in ('contests', 'rows', 'titles'):  # сгенерированные папки пересоздаём, чтобы не копился мусор
        shutil.rmtree(os.path.join(ASSETS, sub), ignore_errors=True)

    from_contests = sum(p['status'] == 'done' for c in contests for p in c['problems'])
    total = from_contests + len(algorithms)
    soon = [p['letter'] for p in (contests[0]['problems'] if contests else []) if p['status'] != 'done']

    banner(total)
    stats(total, from_contests, len(algorithms), contests, soon)
    has_editorials = False
    for c in contests:
        contest_card(c)
        for p in c['problems']:
            problem_row(c, p)
        has_editorials |= editorials(c)
    button('btn-python', 'Код', 'Python', True)
    button('btn-cpp', 'Код', 'C++', True)
    button('btn-soon', 'Скоро', 'в работе', False)
    algo_rows = [algorithm_row(a) for a in algorithms]
    title('contests', 'Контесты', ['Нажми на задачу — откроется условие, на «Код» — решение.',
                                   '«Решена» — проходит все примеры из условия, проверяется автоматически.'])
    title('editorials', 'Разборы', ['Идея и сложность каждого решения.'])
    title('algorithms', 'Алгоритмы', ['Классика, написанная своими руками.'])
    title('structure', 'Структура', ['Всё на своих местах.'])
    title('run', 'Запуск', ['Скопировал. Запустил. Готово.'])
    structure(contests)
    terminal()
    footer()
    readme(contests, algorithms, algo_rows, total, has_editorials)

    for c in contests:
        print(c['slug'] + ': ' + '  '.join(f'{p["letter"]}={STATUS[p["status"]]["label"]}' for p in c['problems']))
    print(f'Решено всего: {total} (контесты {from_contests} + алгоритмы {len(algorithms)})')


if __name__ == '__main__':
    main()
