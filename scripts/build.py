#!/usr/bin/env python3
"""Пересобирает README и картинки в assets/.

1. Прогоняет каждое решение на примерах из tests/ и ставит статус:
   «Решена» — все примеры прошли, «Черновик» — решение есть, но падает, «Скоро» — решения нет.
   Задачи из acmp.ru/ проверяются на примерах из шапки-комментария в самом файле.
2. Считает статистику и рисует карточки в стиле iOS.
3. Собирает две версии: английскую (README.md, картинки в assets/en) — её GitHub показывает по умолчанию,
   и русскую (README.ru.md, картинки в assets). Сверху у обеих — ссылка-переключатель.

Запуск: python3 scripts/build.py  (git-хук запускает его при каждом коммите)
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
from string import Template

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
REPO_URL = 'https://github.com/a1tvv'
OLYMP_URL = 'https://github.com/a1tvv/olymp'
PAGES_URL = 'https://a1tvv.github.io/olymp/'  # живая сетка задач acmp: GitHub Pages из папки docs/
TIME_LIMIT = 10  # секунд на один пример: с запасом, CI-машины бывают медленными
LANG = 'ru'


def tr(ru, en):
    """Текст на языке, который сейчас собирается."""
    return en if LANG == 'en' else ru


MONTHS_EN = {'января': 'January', 'февраля': 'February', 'марта': 'March', 'апреля': 'April', 'мая': 'May',
             'июня': 'June', 'июля': 'July', 'августа': 'August', 'сентября': 'September', 'октября': 'October',
             'ноября': 'November', 'декабря': 'December'}


def date(ru):
    """Дата из contest.json («3 октября 2026») на языке сборки: по-английски — «October 3, 2026»."""
    m = re.fullmatch(r'(\d+) (\S+) (\d+)', ru)
    if LANG == 'ru' or not m or m[2] not in MONTHS_EN:
        return ru
    return f'{MONTHS_EN[m[2]]} {m[1]}, {m[3]}'


def status_label(status):
    return tr(STATUS[status]['label'], STATUS[status]['label_en'])


FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace"
GRAD = {'gray': ('#7c7c80', '#3a3a3c'), 'blue': ('#64d2ff', '#0a84ff'), 'violet': ('#d48cff', '#7d3bd1')}
STATUS = {
    'done': dict(label='Решена', label_en='Solved', color='#30d158'),
    'draft': dict(label='Черновик', label_en='Draft', color='#ff9f0a'),
    'soon': dict(label='Скоро', label_en='Soon', color='#98989d'),
}
ACMP_DIR, ACMP_TOTAL, ACMP_COLS = 'acmp.ru', 2385, 50  # всего задач на acmp.ru
ACMP_HEAD = re.compile(r'// acmp №(\d+) · (.+)')      # первая строка файла
ACMP_LEVEL = re.compile(r'// Сложность: (\d+)%')      # третья строка: сложность с сайта acmp
# решённая задача: чем сложнее, тем ярче зелёный — как в графике коммитов GitHub; (сложность до …%, цвет)
ACMP_GREENS = ((10, '#1a5c2e'), (20, '#1f8a3d'), (35, '#2cb84f'), (101, '#4be36b'))
ACMP_EXAMPLE = re.compile(r'//\s{2,}(.+?)\s+→\s+(.+)')  # «//   2 3 → 5» в шапке; « / » — новая строка
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
    """Задачи из acmp.ru/: номер и название — из первой строки, примеры — из шапки.
    Берём только файлы, которые есть в git, чтобы в README не попали незакоммиченные решения."""
    files = subprocess.run(['git', 'ls-files', ACMP_DIR], cwd=ROOT, capture_output=True, text=True).stdout.split()
    # когда решение коммитили в последний раз: берём коммиты, где менялась ровно одна задача,
    # чтобы общие правки (переносы файлов, новые строки в шапках) не путали «последнюю решённую».
    # git log идёт от новых коммитов к старым, а alias помнит старые имена переименованных файлов
    log = subprocess.run(['git', 'log', '-M', '--format=@%at', '--name-status'],
                         cwd=ROOT, capture_output=True, text=True).stdout
    touched, alias, ts, names = {}, {}, 0, []
    for line in log.splitlines() + ['@0']:
        if line.startswith('@'):
            tasks = {n for n in names if n.startswith(ACMP_DIR + '/') and n.endswith('.cpp')}
            if len(tasks) == 1:
                touched.setdefault(tasks.pop(), ts)
            ts, names = int(line[1:]), []
        elif line:
            status, *paths = line.split('\t')
            current = alias.get(paths[-1], paths[-1])
            if status.startswith('R'):
                alias[paths[0]] = current
            names.append(current)
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
        level = next((int(m[1]) for m in map(ACMP_LEVEL.fullmatch, lines[:5]) if m), None)
        examples = [(m[1].replace(' / ', '\n'), m[2].replace(' / ', '\n'))
                    for m in map(ACMP_EXAMPLE.fullmatch, lines) if m]
        cmd = command(path, workdir)
        ok = cmd and examples and all(passes(cmd, data, out) for data, out in examples)
        problems.append(dict(id=int(head[1]), name=head[2], level=level, file=name, time=touched.get(name, 0),
                             status='done' if ok else 'draft'))
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
    return contests, acmp


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
        f'<text x="816" y="59.5" font-size="18" font-weight="600" fill="#30d158" text-anchor="end">{tr(f"решено {total}", f"{total} solved")}</text></g>'
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
        f'<text x="600" y="206" text-anchor="middle" font-size="28" font-weight="600" fill="url(#aiText)">{tr("Олимпиадное программирование", "Competitive programming")}</text>'
        f'<text x="600" y="318" text-anchor="middle" font-size="104" font-weight="700" letter-spacing="-3" fill="url(#titanium)">{tr("Алтай Абдурахим", "Altay Abdurakhim")}</text>'
        f'<text x="600" y="392" text-anchor="middle" font-size="36" font-weight="600" fill="#86868b">{tr("Алгоритмы. Контесты. Разборы.", "Algorithms. Contests. Explanations.")}</text>'
        f'<text x="600" y="466" text-anchor="middle" font-size="26" font-weight="500" fill="#2997ff">{tr("Смотреть решения ›", "See the solutions ›")}</text>'
    )
    write_svg('banner.svg', 1200, 600, tr('Алтай Абдурахим — олимпиадное программирование',
                                          'Altay Abdurakhim — competitive programming'), defs, body)


def stats(total, from_contests, from_acmp, contests, soon):
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
    soon_body = f'<text x="951" y="344" font-size="24" fill="#ff9f0a">{tr("Скоро", "Soon")}</text>'
    if keys:
        for i, k in enumerate(keys):
            x = 951 + 72 * i
            soon_body += (f'<rect x="{x}" y="378" width="60" height="60" rx="16" fill="#1c1c1e" stroke="#ffffff" stroke-opacity="0.12"/>'
                          f'<text x="{x + 30}" y="419" font-size="{30 if len(k) == 1 else 22}" font-weight="700" '
                          f'fill="#f5f5f7" text-anchor="middle">{esc(k)}</text>')
        soon_body += f'<text x="951" y="490" font-size="22" fill="#86868b">{tr("в работе", "in progress")}</text>'
    else:
        soon_body = (f'<text x="951" y="344" font-size="24" fill="#30d158">{tr("Готово", "Done")}</text>'
                     '<text x="951" y="440" font-size="58" font-weight="700" fill="#30d158">✓</text>'
                     f'<text x="951" y="490" font-size="22" fill="#86868b">{tr("всё решено", "all solved")}</text>')

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
        f'<text x="48" y="86" font-size="24" fill="#86868b">{tr("Решено задач", "Problems solved")}</text>'
        f'<g font-size="{size}" font-weight="700" letter-spacing="-10" fill="url(#ai)">{numbers}</g>'
        f'<text x="48" y="490" font-size="22" fill="#86868b">{from_contests} — {tr("контесты", "contests")}  ·  '
        f'{from_acmp} — acmp</text>'
        '<rect x="610.5" y="0.5" width="589" height="259" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        f'<text x="658" y="86" font-size="24" fill="#86868b">{tr("Контесты", "Contests")}</text>'
        f'<text x="650" y="218" font-size="150" font-weight="700" letter-spacing="-4" fill="url(#blue)">{len(contests)}</text>'
        + contest_name +
        '<rect x="610.5" y="280.5" width="284" height="259" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        f'<text x="646" y="344" font-size="24" fill="#86868b">{tr("Языки", "Languages")}</text>'
        '<text x="644" y="440" font-size="58" font-weight="700" letter-spacing="-1" fill="url(#titanium)">C++17</text>'
        '<text x="646" y="490" font-size="32" fill="#86868b">Python 3</text>'
        '<rect x="915.5" y="280.5" width="284" height="259" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        + soon_body + '</g>'
    )
    label = tr(f'Решено задач: {total} ({from_contests} с контестов, {from_acmp} с acmp). Контестов: {len(contests)}.',
               f'Problems solved: {total} ({from_contests} from contests, {from_acmp} from acmp). Contests: {len(contests)}.')
    if soon:
        label += tr(' Скоро: ', ' Soon: ') + ', '.join(soon) + '.'
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
                  f'<text x="{x + 28:.1f}" y="300" font-size="{label_fs}" fill="{st["color"]}">{status_label(p["status"])}</text></g>')
    defs = TILE + TITANIUM + f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="0">{AI_STOPS}</linearGradient>'
    body = (
        '<rect x="0.5" y="0.5" width="1199" height="369" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        f'<g font-weight="600"><text x="48" y="84" font-size="22" fill="url(#ai)">{esc(c["series"])} · {esc(date(c["date"]))}</text>'
        f'<text x="46" y="146" font-size="54" font-weight="700" letter-spacing="-1.5" fill="url(#titanium)">{esc(c["title"])}</text>'
        f'{chips}</g>'
    )
    summary = '; '.join(f'{p["letter"]} — {status_label(p["status"]).lower()}' for p in probs)
    write_svg(f'contests/{c["slug"]}/card.svg', 1200, 370, f'{c["series"]} {c["title"]}, {date(c["date"])}: {summary}', defs, body)


def cell_color(p):
    """Цвет клетки задачи: решённая — зелёный по сложности (нет сложности — средний), черновик — оранжевый."""
    if p['status'] != 'done':
        return STATUS[p['status']]['color']
    return next(c for limit, c in ACMP_GREENS if (p['level'] or 20) < limit)


def acmp_card(problems):
    """Сетка: по клетке на каждую задачу acmp, решённые горят зелёным.
    В правом верхнем углу — счётчик решённых."""
    solved = [p for p in problems if p['status'] == 'done']
    pitch = 1100 / ACMP_COLS  # сетка во всю ширину карточки
    cell, x0, y0 = round(pitch * 0.82, 1), 52, 196
    rows, tail = divmod(ACMP_TOTAL, ACMP_COLS)  # tail — клетки в последнем, неполном ряду
    grid_h = (rows + (tail > 0)) * pitch - (pitch - cell)
    cells = ''
    for p in problems:
        i = p['id'] - 1
        if i < ACMP_TOTAL:
            cells += (f'<rect x="{x0 + i % ACMP_COLS * pitch:.1f}" y="{y0 + i // ACMP_COLS * pitch:.1f}" width="{cell}" '
                      f'height="{cell}" rx="6" fill="{cell_color(p)}"/>')
    no = tr('№', '#')
    last = max(solved, key=lambda p: p['time'], default=None)
    latest = (f'<tspan fill="#86868b">{tr("Последняя решённая — ", "Last solved — ")}</tspan>{no}{last["id"]} · {esc(last["name"])}'
              if solved else f'<tspan fill="#86868b">{tr("Первая задача — впереди", "The first problem is still ahead")}</tspan>')
    fy = y0 + grid_h + 62
    h = fy + 46
    label = tr(f'Задачи acmp.ru: решено {len(solved)} из {ACMP_TOTAL}',
               f'acmp.ru problems: {len(solved)} of {ACMP_TOTAL} solved')
    defs = (TILE + TITANIUM + f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="0">{AI_STOPS}</linearGradient>'
            f'<pattern id="cell" x="{x0}" y="{y0}" width="{pitch}" height="{pitch}" patternUnits="userSpaceOnUse">'
            f'<rect width="{cell}" height="{cell}" rx="6" fill="#ffffff" fill-opacity="0.06"/></pattern>')
    body = (
        f'<rect x="0.5" y="0.5" width="1199" height="{h - 1}" rx="31.5" fill="url(#tile)" stroke="#ffffff" stroke-opacity="0.1"/>'
        f'<g font-weight="600"><text x="48" y="84" font-size="22" fill="url(#ai)">acmp.ru · {no}1 — {no}{ACMP_TOTAL}</text>'
        f'<text x="46" y="146" font-size="54" font-weight="700" letter-spacing="-1.5" fill="url(#titanium)">{tr("Задачник", "Problem set")}</text>'
        f'<text x="1152" y="146" text-anchor="end"><tspan font-size="54" font-weight="700" letter-spacing="-1.5" fill="url(#ai)">{len(solved)}</tspan>'
        f'<tspan font-size="30" fill="#86868b"> / {ACMP_TOTAL}</tspan></text>'
        f'<rect x="{x0}" y="{y0}" width="{ACMP_COLS * pitch}" height="{rows * pitch}" fill="url(#cell)"/>'
        f'<rect x="{x0}" y="{y0 + rows * pitch}" width="{tail * pitch}" height="{pitch}" fill="url(#cell)"/>{cells}'
        f'<text x="48" y="{fy}" font-size="22" fill="#f5f5f7">{latest}</text>'
        f'<text x="1152" y="{fy}" font-size="22" fill="#86868b" text-anchor="end">'
        f'{tr(f"осталось {ACMP_TOTAL - len(solved)}", f"{ACMP_TOTAL - len(solved)} left")}</text></g>'
    )
    write_svg('acmp.svg', 1200, h, label, defs, body)


PAGE = Template('''<!doctype html>
<html lang="$lang">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$title</title>
<style>
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: #000; color: #f5f5f7; -webkit-font-smoothing: antialiased;
       font: 600 16px/1.4 -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
main { max-width: 1200px; margin: 0 auto; padding: 40px 16px 64px; }
nav { display: flex; justify-content: space-between; color: #86868b; }
nav a { color: #2997ff; text-decoration: none; }
h1 { margin: 40px 0 6px; font-size: 54px; letter-spacing: -1.2px; line-height: 1.1; color: transparent; width: fit-content;
     background: linear-gradient(90deg, #ff9f0a, #ff375f 35%, #bf5af2 70%, #0a84ff); -webkit-background-clip: text; background-clip: text; }
.sub { color: #8e8e93; font-size: 20px; font-weight: 500; margin: 0; }
.card { margin-top: 28px; padding: 40px 48px 34px; border-radius: 32px; border: 1px solid rgba(255,255,255,.1);
        background: linear-gradient(#161618, #000); }
.head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
.label { font-size: 20px; color: transparent; width: fit-content;
         background: linear-gradient(90deg, #ff9f0a, #ff375f 35%, #bf5af2 70%, #0a84ff); -webkit-background-clip: text; background-clip: text; }
.site { font-size: 54px; font-weight: 700; letter-spacing: -1.5px; line-height: 1.15; color: transparent;
        background: linear-gradient(#fff 20%, #8e8e93); -webkit-background-clip: text; background-clip: text; }
.right { text-align: right; }
.count { font-size: 30px; color: #86868b; line-height: 1.15; }
.count b { font-size: 54px; font-weight: 700; letter-spacing: -1.5px; color: transparent;
           background: linear-gradient(90deg, #ff9f0a, #ff375f 35%, #bf5af2 70%, #0a84ff); -webkit-background-clip: text; background-clip: text; }
.grid { display: grid; grid-template-columns: repeat($cols, 1fr); gap: 4px; margin-top: 34px; }
.grid > * { display: block; aspect-ratio: 1; border-radius: 24%; background: rgba(255,255,255,.06); transition: transform .12s; }
.grid > *:hover { transform: scale(1.4); position: relative; z-index: 1; box-shadow: 0 0 0 2px #f5f5f7; }
.foot { display: flex; justify-content: space-between; gap: 16px; margin-top: 28px; color: #86868b; font-size: 18px; }
.foot b { color: #f5f5f7; }
#tip { position: fixed; z-index: 2; pointer-events: none; opacity: 0; transition: opacity .1s; white-space: nowrap;
       padding: 10px 14px; border-radius: 14px; background: rgba(28,28,30,.92); border: 1px solid rgba(255,255,255,.14);
       -webkit-backdrop-filter: blur(20px); backdrop-filter: blur(20px); box-shadow: 0 8px 30px rgba(0,0,0,.5); }
#tip small { display: block; color: #86868b; font-size: 14px; font-weight: 500; }
@media (max-width: 760px) {
  h1 { font-size: 36px; } .sub { font-size: 16px; }
  .card { padding: 22px 16px; border-radius: 22px; } .head { flex-wrap: wrap; } .right { text-align: left; }
  .site, .count b { font-size: 34px; } .count { font-size: 20px; } .label { font-size: 15px; }
  .grid { gap: 2px; margin-top: 20px; } .foot { font-size: 14px; flex-direction: column; gap: 4px; }
}
</style>
</head>
<body>
<main>
<nav><a href="$repo">‹ olymp</a><span>$switch</span></nav>
<h1>$heading</h1>
<p class="sub">$sub</p>
<div class="card">
  <div class="head">
    <div><div class="label">$label</div><div class="site">$site</div></div>
    <div class="right"><div class="count"><b>$solved</b> / $total</div></div>
  </div>
  <div class="grid" id="grid"></div>
  <div class="foot"><div>$latest</div><div>$left</div></div>
</div>
</main>
<div id="tip"></div>
<script>
var DATA = $data, T = $strings, TOTAL = $total;
var grid = document.getElementById('grid'), tip = document.getElementById('tip');
for (var i = 1; i <= TOTAL; i++) {
  var p = DATA[i], el = document.createElement(p ? 'a' : 'i');
  if (p) { el.href = p.url; el.style.background = p.color; }
  el.dataset.id = i;
  grid.appendChild(el);
}
function show(e) {
  var id = e.target.dataset.id;
  if (!id) { tip.style.opacity = 0; return; }
  var p = DATA[id], title = document.createElement('div'), note = document.createElement('small');
  title.textContent = T.task + ' ' + id + (p ? ' · ' + p.name : '');
  note.textContent = !p ? T.todo : p.status !== 'done' ? T.draft
                   : (p.level != null ? T.level + ' ' + p.level + '% · ' : '') + T.open;
  tip.replaceChildren(title, note);
  var x = e.clientX + 16, y = e.clientY + 18;
  if (x + tip.offsetWidth > innerWidth - 8) x = e.clientX - tip.offsetWidth - 16;
  if (y + tip.offsetHeight > innerHeight - 8) y = e.clientY - tip.offsetHeight - 16;
  tip.style.left = x + 'px'; tip.style.top = y + 'px'; tip.style.opacity = 1;
}
grid.addEventListener('mousemove', show);
grid.addEventListener('mouseleave', function () { tip.style.opacity = 0; });
</script>
</body>
</html>
''')


def acmp_page(problems):
    """Живая сетка задач acmp для GitHub Pages: у курсора — номер и название задачи, клик — файл с решением.
    В README картинка неинтерактивна, поэтому карточка ведёт сюда. Английская — docs/index.html, русская — docs/ru/."""
    solved = [p for p in problems if p['status'] == 'done']
    data = {p['id']: dict(name=p['name'], level=p['level'], status=p['status'], color=cell_color(p),
                          url=f'{OLYMP_URL}/blob/main/{p["file"]}') for p in problems}
    strings = dict(task=tr('Задача', 'Problem'), level=tr('Сложность', 'Difficulty'),
                   open=tr('открыть решение ›', 'open the solution ›'),
                   draft=tr('черновик: пока не проходит примеры ›', 'draft: does not pass the examples yet ›'),
                   todo=tr('ещё не решена', 'not solved yet'))
    no = tr('№', '#')
    last = max(solved, key=lambda p: p['time'], default=None)
    latest = (f'{tr("Последняя решённая — ", "Last solved — ")}<b>{no}{last["id"]} · {esc(last["name"])}</b>'
              if solved else tr('Первая задача — впереди', 'The first problem is still ahead'))
    page = PAGE.substitute(
        lang=LANG, title='acmp.ru · olymp', cols=ACMP_COLS, total=ACMP_TOTAL,
        repo=OLYMP_URL if LANG == 'en' else f'{OLYMP_URL}/blob/main/README.ru.md',
        switch=('<a href="../">English</a> &nbsp;|&nbsp; Русский' if LANG == 'ru' else 'English &nbsp;|&nbsp; <a href="ru/">Русский</a>'),
        heading='acmp.ru', site=tr('Задачник', 'Problem set'),
        sub=tr('Наведи на клетку — увидишь задачу. Нажми — откроется решение.',
               'Hover over a cell to see the problem. Click it to open the solution.'),
        label=f'acmp.ru · {no}1 — {no}{ACMP_TOTAL}', solved=len(solved),
        latest=latest, left=tr(f'осталось {ACMP_TOTAL - len(solved)}', f'{ACMP_TOTAL - len(solved)} left'),
        data=json.dumps(data, ensure_ascii=False).replace('</', '<\\/'), strings=json.dumps(strings, ensure_ascii=False))
    path = os.path.join(ROOT, 'docs', *(['ru'] if LANG == 'ru' else []), 'index.html')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(page)


def title(name, heading, subs):
    defs = f'<linearGradient id="ai" x1="0" y1="0" x2="1" y2="0">{AI_STOPS}</linearGradient>'
    body = f'<text x="2" y="62" font-size="54" font-weight="700" letter-spacing="-1.2" fill="url(#ai)">{esc(heading)}</text>'
    for i, sub in enumerate(subs):
        body += f'<text x="3" y="{104 + 34 * i}" font-size="25" font-weight="500" fill="#8e8e93">{esc(sub)}</text>'
    write_svg(f'titles/{name}.svg', 1200, 92 + 34 * len(subs), heading, defs, body)


def structure(contests):
    tree = [(0, 'olymp/', '')]
    for c in contests:
        tree += [(1, c['slug'] + '/', ''), (2, 'statements/', tr('условия задач (PDF)', 'problem statements (PDF)')),
                 (2, 'solutions/', tr('решения: A.py, B.py, …', 'solutions: A.py, B.py, …')),
                 (2, 'tests/', tr('примеры из условий', 'examples from the problems')),
                 (2, 'contest.json', tr('названия, темы, разборы', 'names, topics, explanations'))]
    tree += [(1, 'acmp.ru/', tr('задачи acmp.ru: 0001.cpp, 0002.cpp, …', 'acmp.ru problems: 0001.cpp, 0002.cpp, …')),
             (1, 'scripts/', tr('сборка README и проверка решений', 'README build and solution checks')),
             (1, 'assets/', tr('картинки для README', 'pictures for README'))]
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
            + rich(48, ny, tr('Новый контест — новая папка `<год>-<название>/` в корне с такой же структурой',
                              'New contest — a new folder `<year>-<name>/` in the root with the same structure'), fs=20)
            + rich(48, ny + 36, tr('Статистика считается сама: при коммите решения прогоняются на примерах из условий',
                                   'Stats update by themselves: on each commit, solutions run on the examples from the problems'), fs=20))
    write_svg('structure.svg', 1200, h, tr('Структура репозитория', 'Repository structure'), defs, body)


def terminal():
    p, t, op, s, com, out = '#30d158', '#f5f5f7', '#ff375f', '#ffd60a', '#636366', '#64d2ff'
    lines = [
        [('# Python', com)],
        [('$ ', p), ('python3 2026-icpc-qual/solutions/D.py ', t), ('<<<', op), (' 34', t)],
        [('8 15', out)], [],
        [('# C++', com)],
        [('$ ', p), ('clang++ -std=c++17 -O2 acmp.ru/1231.cpp -o bubble', t)],
        [('$ ', p), ('echo ', t), ('"4  4 2 3 1"', s), (' | ', op), ('./bubble', t)],
        [('5', out)], [],
        [(tr('# Пересобрать README вручную', '# Rebuild README by hand'), com)],
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
    write_svg('run.svg', 1200, h, tr('Запуск решений в терминале', 'Running solutions in the terminal'), TILE, body)


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

def section_title(anchor, name, alt, img):
    return f'<a name="{anchor}"></a>\n<img src="{img}/titles/{name}.svg" alt="{alt}" width="100%">\n'


def readme(contests, acmp_solved, total):
    img = 'assets' if LANG == 'ru' else 'assets/en'  # цитата и футер — общие, лежат в assets
    switch = ('<p align="center"><a href="README.md">English</a> &nbsp;|&nbsp; <b>Русский</b></p>' if LANG == 'ru' else
              '<p align="center"><b>English</b> &nbsp;|&nbsp; <a href="README.ru.md">Русский</a></p>')
    out = [
        tr('<!-- Этот файл собирается автоматически: python3 scripts/build.py. Правки вручную перезапишутся. -->',
           '<!-- This file is built automatically: python3 scripts/build.py. Edits by hand will be lost. -->'),
        switch,
        '',
        f'<a href="#contests"><img src="{img}/banner.svg" alt="'
        f'{tr("Алтай Абдурахим — олимпиадное программирование", "Altay Abdurakhim — competitive programming")}" width="100%"></a>',
        '',
        f'<p align="center">\n  <a href="#contests">{tr("Контесты", "Contests")}&nbsp;›</a>&emsp;\n'
        f'  <a href="#acmp">acmp.ru&nbsp;›</a>&emsp;\n'
        f'  <a href="#structure">{tr("Структура", "Structure")}&nbsp;›</a>&emsp;\n'
        f'  <a href="#run">{tr("Запуск", "Run")}&nbsp;›</a>\n</p>',
        '', '<br>', '',
        f'<img src="{img}/stats.svg" alt="{tr("Решено задач", "Problems solved")}: {total}" width="100%">',
        '', '<br>\n<br>', '',
        '<img src="assets/quote.svg" alt="Talk is cheap. Show me the code. — Linus Torvalds" width="100%">',
        '', '<br>', '',
        section_title('contests', 'contests', tr('Контесты', 'Contests'), img),
    ]
    for c in contests:
        out.append(f'<a href="{c["slug"]}"><img src="{img}/contests/{c["slug"]}/card.svg" '
                   f'alt="{esc(c["series"])} {esc(c["title"])}, {esc(date(c["date"]))}" width="100%"></a>\n')
    out += ['<br>\n<br>\n',
            section_title('acmp', 'acmp', 'acmp.ru', img),
            f'<a href="{PAGES_URL}{"ru/" if LANG == "ru" else ""}"><img src="{img}/acmp.svg" alt="'
            + tr(f'Задачи acmp.ru: решено {acmp_solved} из {ACMP_TOTAL}',
                 f'acmp.ru problems: {acmp_solved} of {ACMP_TOTAL} solved')
            + '" width="100%"></a>\n',
            '<br>\n<br>\n',
            section_title('structure', 'structure', tr('Структура', 'Structure'), img),
            f'<img src="{img}/structure.svg" alt="{tr("Структура репозитория", "Repository structure")}" width="100%">',
            '', '<br>\n<br>', '',
            section_title('run', 'run', tr('Запуск', 'Run'), img),
            f'<img src="{img}/run.svg" alt="{tr("Запуск решений в терминале", "Running solutions in the terminal")}" width="100%">',
            '',
            f'<details>\n<summary>{tr("Скопировать команды", "Copy the commands")}</summary>\n<br>\n\n```bash\n# Python\n'
            'python3 2026-icpc-qual/solutions/D.py <<< 34\n# 8 15\n\n# C++\n'
            'clang++ -std=c++17 -O2 acmp.ru/1231.cpp -o bubble\necho "4  4 2 3 1" | ./bubble\n# 5\n\n'
            f'{tr("# Пересобрать README вручную", "# Rebuild README by hand")}\npython3 scripts/build.py\n```\n\n</details>',
            '', '<br>', '',
            '<img src="assets/footer.svg" alt="Stay hungry. Stay foolish. — Steve Jobs, 1955–2011" width="100%">',
            '',
            f'<p align="center">\n  <sub>{tr("Сделано с ☕ и", "Made with ☕ and")} <code>-O2</code> &nbsp;·&nbsp; '
            f'<a href="{REPO_URL}">@a1tvv</a></sub>\n</p>', '']
    with open(os.path.join(ROOT, 'README.ru.md' if LANG == 'ru' else 'README.md'), 'w') as f:
        f.write('\n'.join(out))


def build(lang, contests, acmp):
    """Рисует картинки и README на одном языке: 'ru' — assets и README.ru.md, 'en' — assets/en и README.md."""
    global LANG, ASSETS
    LANG = lang
    ASSETS = os.path.join(ROOT, 'assets') if lang == 'ru' else os.path.join(ROOT, 'assets', 'en')
    for sub in ('contests', 'titles'):  # сгенерированные папки пересоздаём, чтобы не копился мусор
        shutil.rmtree(os.path.join(ASSETS, sub), ignore_errors=True)

    from_contests = sum(p['status'] == 'done' for c in contests for p in c['problems'])
    from_acmp = sum(p['status'] == 'done' for p in acmp)
    total = from_contests + from_acmp
    soon = [p['letter'] for p in (contests[0]['problems'] if contests else []) if p['status'] != 'done']

    banner(total)
    stats(total, from_contests, from_acmp, contests, soon)
    for c in contests:
        contest_card(c)
    acmp_card(acmp)
    acmp_page(acmp)
    title('contests', tr('Контесты', 'Contests'),
          [tr('Нажми на карточку — откроются условия и решения.', 'Click a card to open the problems and solutions.'),
           tr('«Решена» — проходит все примеры из условия, проверяется автоматически.',
              '“Solved” means it passes all examples from the problem. This is checked automatically.')])
    title('acmp', 'acmp.ru',
          [tr(f'Все задачи acmp.ru по порядку, от №1 до №{ACMP_TOTAL}. Нажми на карточку — откроются решения.',
              f'All acmp.ru problems in order, from #1 to #{ACMP_TOTAL}. Click the card to open the solutions.'),
           tr('Каждая клетка — задача. Зелёная — решена: чем ярче, тем сложнее задача.',
              'Each cell is a problem. Green means solved: the brighter, the harder the problem.')])
    title('structure', tr('Структура', 'Structure'), [tr('Всё на своих местах.', 'Everything in its place.')])
    title('run', tr('Запуск', 'Run'), [tr('Скопировал. Запустил. Готово.', 'Copy. Run. Done.')])
    structure(contests)
    terminal()
    if lang == 'ru':  # в цитате и футере нет русского текста — они общие для обеих версий
        quote()
        footer()
    readme(contests, from_acmp, total)
    return from_contests, from_acmp, total


def main():
    contests, acmp = load()
    build('ru', contests, acmp)
    from_contests, from_acmp, total = build('en', contests, acmp)

    for c in contests:
        print(c['slug'] + ': ' + '  '.join(f'{p["letter"]}={STATUS[p["status"]]["label"]}' for p in c['problems']))
    print('acmp: ' + ('  '.join(f'№{p["id"]}={STATUS[p["status"]]["label"]}' for p in acmp) or 'пока пусто'))
    print(f'Решено всего: {total} (контесты {from_contests} + acmp {from_acmp})')


if __name__ == '__main__':
    main()
