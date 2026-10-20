"""Чекер E: подходит любая перестановка 1..N, на которой сортировка вставками делает ровно K обменов.

Число обменов сортировки вставками равно числу инверсий — считаем его деревом Фенвика.
Запуск: python3 check.py <файл.in> < вывод_решения; код возврата 0 — ответ верный.
"""
import sys

n, k = map(int, open(sys.argv[1]).read().split())
try:
    a = list(map(int, sys.stdin.read().split()))
except ValueError:
    sys.exit(1)
if len(a) != n or sorted(a) != list(range(1, n + 1)):
    sys.exit(1)

tree = [0] * (n + 1)
inversions = 0
for i, x in enumerate(a):
    not_greater, j = 0, x
    while j:
        not_greater += tree[j]
        j -= j & -j
    inversions += i - not_greater
    j = x
    while j <= n:
        tree[j] += 1
        j += j & -j
sys.exit(0 if inversions == k else 1)
