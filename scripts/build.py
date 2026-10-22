#!/usr/bin/env python3
"""Пересобирает README.md и картинки в assets/.

1. Прогоняет каждое решение на примерах из tests/ и ставит статус:
   «Решена» — все примеры прошли, «Черновик» — решение есть, но падает, «Скоро» — решения нет.
   Задачи acmp из first_1000/ проверяются на примерах из шапки-комментария в самом файле.
2. Считает статистику и рисует карточки в стиле iOS.

Запуск: python3 scripts/build.py  (то же самое делает git-хук при каждом коммите)
"""
import glob
import html
import json
import os
import re
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
GRAD = {'gray': ('#7c7c80', '#3a3a3c'), 'blue': ('#64d2ff', '#0a84ff'), 'violet': ('#d48cff', '#7d3bd1')}
STATUS = {
    'done': dict(label='Решена', color='#30d158'),
    'draft': dict(label='Черновик', color='#ff9f0a'),
    'soon': dict(label='Скоро', color='#98989d'),
}
ACMP_DIR, ACMP_TOTAL, ACMP_COLS = 'first_1000', 1000, 50
ACMP_HEAD = re.compile(r'// acmp №(\d+) · (.+)')      # первая строка файла
ACMP_EXAMPLE = re.compile(r'//\s{2,}(.+?)\s+→\s+(.+)')  # «//   2 3 → 5» в шапке
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


def command(solution, workdir):
    """Как запустить решение; None, если C++ не скомпилировался."""
    if not solution.endswith('.cpp'):
        return [sys.executable, solution]
    compiler = shutil.which('g++') or shutil.which('clang++')
    exe = os.path.join(workdir, os.path.splitext(os.path.basename(solution))[0])
    if not compiler or subprocess.run([compiler, '-std=c++17', '-O2', solution, '-o', exe],
                                      capture_output=True).returncode:
        return None
    return [exe]


def judge(cdir, letter, workdir):
    solution = find_solution(cdir, letter)
    if not solution:
        return 'soon'
    cmd = command(solution, workdir)
    if not cmd:
        return 'draft'

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


def passes(cmd, data, expected):
    try:
        result = run(cmd, data + '\n')
    except subprocess.TimeoutExpired:
        return False
    return result.returncode == 0 and result.stdout.split() == expected.split()


def load_acmp(workdir):
    """Задачи acmp из first_1000/: номер и название — из первой строки, примеры — из шапки.
    Берём только файлы, которые есть в git, чтобы в README не попали незакоммиченные решения."""
    files = subprocess.run(['git', 'ls-files', ACMP_DIR], cwd=ROOT, capture_output=True, text=True).stdout.split()
    problems = []
    for name in files:
        path = os.path.join(ROOT, name)
        if not name.endswith('.cpp') or not os.path.isfile(path):
            continue
        with open(path) as f:
            lines = f.read().splitlines()
        head = ACMP_HEAD.fullmatch(lines[0]) if lines else None
        if not head:
            continue
        examples = [m.groups() for m in map(ACMP_EXAMPLE.fullmatch, lines) if m]
        cmd = command(path, workdir)
        ok = cmd and examples and all(passes(cmd, data, out) for data, out in examples)
        problems.append(dict(id=int(head[1]), name=head[2], status='done' if ok else 'draft'))
    return sorted(problems, key=lambda p: p['id'])


def load():
    contests = []
    with tempfile.TemporaryDirectory() as workdir:
        for path in sorted(glob.glob(os.path.join(ROOT, '*', 'contest.json')), reverse=True):
            cdir = os.path.dirname(path)
            with open(path) as f:
                contest = json.load(f)
            contest['slug'] = os.path.basename(cdir)
            for p in contest['problems']:
                p['status'] = judge(cdir, p['letter'], workdir)
            contests.append(contest)
        acmp = load_acmp(workdir)
    with open(os.path.join(ROOT, 'algorithms', 'algorithms.json')) as f:
        algorithms = json.load(f)
    return contests, algorithms, acmp


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


def stats(total, from_contests, from_algorithms, from_acmp, contests, soon):
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
        f'<text x="48" y="490" font-size="22" fill="#86868b">{from_contests} — контесты  ·  {from_algorithms} — алгоритмы  ·  {from_acmp} — acmp</text>'
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
    label = (f'Решено задач: {total} ({from_contests} с контестов, {from_algorithms} из алгоритмов, '
             f'{from_acmp} с acmp). Контестов: {len(contests)}.')
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


def acmp_card(problems):
    """Сетка из 1000 клеток — по одной на задачу acmp №1…№1000; решённые горят зелёным."""
    solved = [p for p in problems if p['status'] == 'done']
    pitch, cell, x0, y0 = 22, 18, 52, 196
    rows = ACMP_TOTAL // ACMP_COLS
    grid_h = rows * pitch - (pitch - cell)
    cells = ''
    for p in problems:
        i = p['id'] - 1
        if i < ACMP_TOTAL:
            cells += (f'<rect x="{x0 + i % ACMP_COLS * pitch}" y="{y0 + i // ACMP_COLS * pitch}" width="{cell}" '
                      f'height="{cell}" rx="5" fill="{STATUS[p["status"]]["color"]}"/>')
    latest = (f'<tspan fill="#86868b">Последняя решённая — </tspan>№{solved[-1]["id"]} · {esc(solved[-1]["name"])}'
              if solved else '<tspan fill="#86868b">Первая задача — впереди</tspan>')
    fy = y0 + grid_h + 62
    h = fy + 46
    defs = (TILE + TITANIUM + f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="0">{AI_STOPS}</linearGradient>'
            f'<pattern id="cell" x="{x0}" y="{y0}" width="{pitch}" height="{pitch}" patternUnits="userSpaceOnUse">'
            f'<rect width="{cell}" height="{cell}" rx="5" fill="#ffffff" fill-opacity="0.06"/></pattern>')
    body = (
        f'<rect x="0.5" y="0.5" width="1199" height="{h - 1}" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        f'<g font-weight="600"><text x="48" y="84" font-size="22" fill="url(#ai)">Задачник · №1 — №{ACMP_TOTAL}</text>'
        '<text x="46" y="146" font-size="54" font-weight="700" letter-spacing="-1.5" fill="url(#titanium)">acmp.ru</text>'
        f'<text x="1152" y="146" text-anchor="end"><tspan font-size="54" font-weight="700" letter-spacing="-1.5" fill="url(#ai)">{len(solved)}</tspan>'
        f'<tspan font-size="30" fill="#86868b"> / {ACMP_TOTAL}</tspan></text>'
        f'<rect x="{x0}" y="{y0}" width="{ACMP_COLS * pitch}" height="{rows * pitch}" fill="url(#cell)"/>{cells}'
        f'<text x="48" y="{fy}" font-size="22" fill="#f5f5f7">{latest}</text>'
        f'<text x="1152" y="{fy}" font-size="22" fill="#86868b" text-anchor="end">осталось {ACMP_TOTAL - len(solved)}</text></g>'
    )
    write_svg('first_1000.svg', 1200, h, f'Первые 1000 задач acmp.ru: решено {len(solved)} из {ACMP_TOTAL}', defs, body)


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
    for c in contests:
        tree += [(1, c['slug'] + '/', ''), (2, 'statements/', 'условия задач (PDF)'),
                 (2, 'solutions/', 'решения: A.py, B.py, …'), (2, 'tests/', 'примеры из условий'),
                 (2, 'contest.json', 'названия, темы, разборы')]
    tree += [(1, 'first_1000/', 'задачи acmp.ru: 0001.cpp, 0002.cpp, …'),
             (1, 'algorithms/', 'классические алгоритмы'), (1, 'scripts/', 'сборка README и проверка решений'),
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
            + rich(48, ny, 'Новый контест — новая папка `<год>-<название>/` в корне с такой же структурой', fs=20)
            + rich(48, ny + 36, 'Статистика считается сама: при коммите решения прогоняются на примерах из условий', fs=20))
    write_svg('structure.svg', 1200, h, 'Структура репозитория', defs, body)


def terminal():
    p, t, op, s, com, out = '#30d158', '#f5f5f7', '#ff375f', '#ffd60a', '#636366', '#64d2ff'
    lines = [
        [('# Python', com)],
        [('$ ', p), ('python3 2026-icpc-qual/solutions/D.py ', t), ('<<<', op), (' 34', t)],
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


def quote():
    defs = (TITANIUM + f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="0">{AI_STOPS}'
            '<animateTransform attributeName="gradientTransform" type="translate" values="-0.3 0;0.3 0;-0.3 0" dur="8s" repeatCount="indefinite"/>'
            '</linearGradient><radialGradient id="spot" cx="0.5" cy="1" r="0.7"><stop offset="0" stop-color="#bf5af2" stop-opacity="0.22"/>'
            '<stop offset="1" stop-color="#bf5af2" stop-opacity="0"/></radialGradient>'
            '<clipPath id="card"><rect width="1200" height="380" rx="32"/></clipPath>')
    body = ('<g clip-path="url(#card)"><rect width="1200" height="380" fill="#000000"/><rect width="1200" height="380" fill="url(#spot)"/></g>'
            '<rect x="0.5" y="0.5" width="1199" height="379" rx="31.5" fill="none" stroke="#ffffff" stroke-opacity="0.1"/>'
            '<g font-weight="700" text-anchor="middle">'
            '<text x="600" y="160" font-size="96" letter-spacing="-3" fill="url(#titanium)">Talk is cheap.</text>'
            '<text x="600" y="262" font-size="96" letter-spacing="-3" fill="url(#ai)">Show me the code.</text>'
            '<text x="600" y="326" font-size="22" font-weight="600" fill="#86868b">Linus Torvalds · LKML, 2000</text></g>')
    write_svg('quote.svg', 1200, 380, 'Talk is cheap. Show me the code. — Linus Torvalds', defs, body)


# ───────────────────────── README ─────────────────────────

def section_title(anchor, name, alt):
    return f'<a name="{anchor}"></a>\n<img src="assets/titles/{name}.svg" alt="{alt}" width="100%">\n'


def readme(contests, algorithms, algo_rows, acmp_solved, total):
    out = [
        '<!-- Этот файл собирается автоматически: python3 scripts/build.py. Правки вручную перезапишутся. -->',
        '<a href="#contests"><img src="assets/banner.svg" alt="Алтай Абдурахим — олимпиадное программирование" width="100%"></a>',
        '',
        '<p align="center">\n  <a href="#contests">Контесты&nbsp;›</a>&emsp;\n  <a href="#first-1000">Первые 1000&nbsp;›</a>&emsp;\n'
        '  <a href="#algorithms">Алгоритмы&nbsp;›</a>&emsp;\n  <a href="#structure">Структура&nbsp;›</a>&emsp;\n'
        '  <a href="#run">Запуск&nbsp;›</a>\n</p>',
        '', '<br>', '',
        f'<img src="assets/stats.svg" alt="Решено задач: {total}" width="100%">',
        '', '<br>\n<br>', '',
        '<img src="assets/quote.svg" alt="Talk is cheap. Show me the code. — Linus Torvalds" width="100%">',
        '', '<br>', '',
        section_title('contests', 'contests', 'Контесты'),
    ]
    for c in contests:
        out.append(f'<a href="{c["slug"]}"><img src="assets/contests/{c["slug"]}/card.svg" '
                   f'alt="{esc(c["series"])} {esc(c["title"])}, {esc(c["date"])}" width="100%"></a>\n')
    out += ['<br>\n<br>\n',
            section_title('first-1000', 'first_1000', 'Первые 1000'),
            f'<a href="{ACMP_DIR}"><img src="assets/first_1000.svg" alt="Первые 1000 задач acmp.ru: '
            f'решено {acmp_solved} из {ACMP_TOTAL}" width="100%"></a>\n',
            '<br>\n<br>\n']
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
            'python3 2026-icpc-qual/solutions/D.py <<< 34\n# 8 15\n\n# C++\n'
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
    contests, algorithms, acmp = load()
    for sub in ('contests', 'rows', 'titles'):  # сгенерированные папки пересоздаём, чтобы не копился мусор
        shutil.rmtree(os.path.join(ASSETS, sub), ignore_errors=True)

    from_contests = sum(p['status'] == 'done' for c in contests for p in c['problems'])
    from_acmp = sum(p['status'] == 'done' for p in acmp)
    total = from_contests + len(algorithms) + from_acmp
    soon = [p['letter'] for p in (contests[0]['problems'] if contests else []) if p['status'] != 'done']

    banner(total)
    stats(total, from_contests, len(algorithms), from_acmp, contests, soon)
    for c in contests:
        contest_card(c)
    acmp_card(acmp)
    algo_rows = [algorithm_row(a) for a in algorithms]
    title('contests', 'Контесты', ['Нажми на карточку — откроются условия и решения.',
                                   '«Решена» — проходит все примеры из условия, проверяется автоматически.'])
    title('first_1000', 'Первые 1000', ['Задачи acmp.ru по порядку — от №1 до №1000.',
                                        'Каждая клетка — задача, зелёная — решена.'])
    title('algorithms', 'Алгоритмы', ['Классика, написанная своими руками.'])
    title('structure', 'Структура', ['Всё на своих местах.'])
    title('run', 'Запуск', ['Скопировал. Запустил. Готово.'])
    structure(contests)
    terminal()
    quote()
    footer()
    readme(contests, algorithms, algo_rows, from_acmp, total)

    for c in contests:
        print(c['slug'] + ': ' + '  '.join(f'{p["letter"]}={STATUS[p["status"]]["label"]}' for p in c['problems']))
    print('acmp: ' + ('  '.join(f'№{p["id"]}={STATUS[p["status"]]["label"]}' for p in acmp) or 'пока пусто'))
    print(f'Решено всего: {total} (контесты {from_contests} + алгоритмы {len(algorithms)} + acmp {from_acmp})')


if __name__ == '__main__':
    main()
