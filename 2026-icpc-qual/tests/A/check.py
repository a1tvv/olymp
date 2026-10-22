"""Чекер A: первая строка — число соревнований, остальные строки можно выводить в любом порядке.

Запуск: python3 check.py <файл.in> < вывод_решения; код возврата 0 — ответ верный.
"""
import sys

expected = open(sys.argv[1][:-3] + '.out').read().strip().splitlines()
got = sys.stdin.read().strip().splitlines()

ok = (bool(got) and got[0].strip() == expected[0].strip()
      and sorted(s.strip() for s in got[1:]) == sorted(s.strip() for s in expected[1:]))
sys.exit(0 if ok else 1)
