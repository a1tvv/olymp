"""Чекер A: подходит любой обмен, после которого k-е по величине f_i максимально.

Перебирает все обмены (n ≤ 100) и сравнивает лучший результат с результатом обмена из ответа.
Запуск: python3 check.py <файл.in> < вывод_решения; код возврата 0 — ответ верный.
"""
import sys


def kth(a, k):
    """k-е по величине среди f_i = mex(a_1..a_i)."""
    seen, mex, f = set(), 0, []
    for x in a:
        seen.add(x)
        while mex in seen:
            mex += 1
        f.append(mex)
    return sorted(f, reverse=True)[k - 1]


data = open(sys.argv[1]).read().split()
answers = sys.stdin.read().strip().splitlines()
t, pos = int(data[0]), 1
if len(answers) != t:
    sys.exit(1)
for line in answers:
    n, k = int(data[pos]), int(data[pos + 1])
    a = list(map(int, data[pos + 2:pos + 2 + n]))
    pos += 2 + n
    best = kth(a, k)
    for i in range(n):
        for j in range(i + 1, n):
            b = a[:]
            b[i], b[j] = b[j], b[i]
            best = max(best, kth(b, k))
    words = line.split()
    if words == ['-1']:
        got = kth(a, k)
    elif len(words) == 2 and all(w.lstrip('-').isdigit() for w in words):
        i, j = int(words[0]) - 1, int(words[1]) - 1
        if not (0 <= i < n and 0 <= j < n and i != j):
            sys.exit(1)
        b = a[:]
        b[i], b[j] = b[j], b[i]
        got = kth(b, k)
    else:
        sys.exit(1)
    if got != best:
        sys.exit(1)
sys.exit(0)
