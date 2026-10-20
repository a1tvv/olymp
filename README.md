<a href="#контесты"><img src="assets/banner.svg" alt="Алтай Абдурахим — олимпиадное программирование" width="100%"></a>

<p align="center">
  <a href="#контесты">Контесты&nbsp;›</a>&emsp;
  <a href="#разборы">Разборы&nbsp;›</a>&emsp;
  <a href="#алгоритмы">Алгоритмы&nbsp;›</a>&emsp;
  <a href="#структура">Структура&nbsp;›</a>&emsp;
  <a href="#запуск">Запуск&nbsp;›</a>
</p>

<br>

<img src="assets/stats.svg" alt="Решено задач: 4 (3 с контеста ICPC, 1 из алгоритмов). Контестов: 1. Языки: C++17, Python 3. Скоро: C, E, H" width="100%">

<br>
<br>

<p align="center">
  <i>«Talk is cheap. Show me the code.»</i><br>
  <sub>— Linus Torvalds</sub>
</p>

<br>

## Контесты

Каждая задача: условие, решение и разбор.

<img src="assets/icpc-kg-qual-2026.svg" alt="ICPC NERC Kyrgyzstan Qualification, 3 октября 2026: A, B, D решены; C — черновик; E, H — скоро" width="100%">

| | Задача | Темы | Решение | Статус |
|:-:|:--|:--|:-:|:-:|
| <kbd>A</kbd> | [Немного истории](contests/2026-icpc-kyrgyzstan-qual/statements/A.pdf) | `реализация` | [![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](contests/2026-icpc-kyrgyzstan-qual/solutions/A.py) | ![Решена](https://img.shields.io/badge/%D0%A0%D0%B5%D1%88%D0%B5%D0%BD%D0%B0-30d158?style=flat-square) |
| <kbd>B</kbd> | [Ответственная стирка](contests/2026-icpc-kyrgyzstan-qual/statements/B.pdf) | `жадность` `группировка` | [![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](contests/2026-icpc-kyrgyzstan-qual/solutions/B.py) | ![Решена](https://img.shields.io/badge/%D0%A0%D0%B5%D1%88%D0%B5%D0%BD%D0%B0-30d158?style=flat-square) |
| <kbd>C</kbd> | [Сизифов труд](contests/2026-icpc-kyrgyzstan-qual/statements/C.pdf) | `математика` | [![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](contests/2026-icpc-kyrgyzstan-qual/solutions/C.py) | ![Черновик](https://img.shields.io/badge/%D0%A7%D0%B5%D1%80%D0%BD%D0%BE%D0%B2%D0%B8%D0%BA-ff9f0a?style=flat-square) |
| <kbd>D</kbd> | [Чат-бот на калькуляторе](contests/2026-icpc-kyrgyzstan-qual/statements/D.pdf) | `перебор` `цифры` | [![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](contests/2026-icpc-kyrgyzstan-qual/solutions/D.py) | ![Решена](https://img.shields.io/badge/%D0%A0%D0%B5%D1%88%D0%B5%D0%BD%D0%B0-30d158?style=flat-square) |
| <kbd>E</kbd> | [Сортировка вставками](contests/2026-icpc-kyrgyzstan-qual/statements/E.pdf) | `конструктив` `инверсии` | — | ![Скоро](https://img.shields.io/badge/%D0%A1%D0%BA%D0%BE%D1%80%D0%BE-8e8e93?style=flat-square) |
| <kbd>H</kbd> | [Каждому префиксу по медиане!](contests/2026-icpc-kyrgyzstan-qual/statements/H.pdf) | `медиана` `кучи` | — | ![Скоро](https://img.shields.io/badge/%D0%A1%D0%BA%D0%BE%D1%80%D0%BE-8e8e93?style=flat-square) |

<sub>«Решена» — проходит все примеры из условия. Название задачи открывает условие в PDF.</sub>

### Разборы

<details>
<summary><b>A · Немного истории</b> &nbsp;<code>O(1)</code></summary>
<br>

- `ICPC Regional` проводится каждый год, начиная с 2005-го.
- `ICPC Qual` — с 2019-го, кроме ковидных 2020 и 2021.
- `School Regional` и `School Qual` впервые проходят в 2026-м.

Хватает трёх условий на год.

</details>

<details>
<summary><b>B · Ответственная стирка</b> &nbsp;<code>O(N)</code></summary>
<br>

- Все носки стираются вместе — максимум **одна** стирка.
- Цвета делятся на группы: `White`, `Yellow`, `Red`, `Green` — каждый сам по себе, а `Black`, `Blue`, `Gray` — общая «тёмная» группа.
- Майки: по одной стирке на каждую группу, где есть хотя бы одна майка.
- Кофты и штаны: группе из $`k`$ вещей нужно $`\lceil k/2 \rceil`$ стирок.

Ответ — сумма по всем пунктам.

</details>

<details>
<summary><b>C · Сизифов труд</b> &nbsp;🚧 черновик</summary>
<br>

Сейчас решение моделирует дни один за другим для одной пары $`A, B`$. Что осталось сделать:

- читать $`Q`$ пар, по паре в строке;
- после $`k`$-го дня Сизиф стоит в точке $`f(k) = kA - B\cdot\frac{k(k-1)}{2}`$;
- $`f(k+1) - f(k) = A - kB`$, значит $`f`$ растёт, пока $`kB \lt A`$, и максимум достигается при $`k = \lceil A/B \rceil`$.

Это $`O(1)`$ на запрос вместо $`\approx A/B`$ шагов: на тесте `987654321 1` симуляция делает около $`10^9`$ итераций.

</details>

<details>
<summary><b>D · Чат-бот на калькуляторе</b> &nbsp;<code>O(N · log N)</code></summary>
<br>

- Перебираем все числа от $`0`$ до $`N`$ и смотрим на множество их цифр.
- Обычный вид: цифры $`\subseteq \{0, 1, 5, 8\}`$.
- Перевёрнутый: цифры $`\subseteq \{0, 1, 3, 5, 7, 8\}`$.

$`N \le 123\,456`$, так что прямой перебор укладывается с большим запасом.

</details>

<br>

## Алгоритмы

Классика, написанная своими руками.

| Алгоритм | Что делает | Сложность | Код |
|:--|:--|:-:|:-:|
| Сортировка пузырьком | Сортирует массив и считает число обменов — оно равно числу инверсий | `O(n²)` | [![C++](https://img.shields.io/badge/C%2B%2B-00599C?style=flat-square&logo=cplusplus&logoColor=white)](algorithms/sorting/bubble_sort_swaps.cpp) |

<br>

## C++ basics

Песочница, в которой разбираю основы языка.

| Файл | О чём |
|:--|:--|
| [`hello.cpp`](cpp-basics/hello.cpp) | Первая программа: функция, вывод, `setlocale` |
| [`f1.cpp`](cpp-basics/f1.cpp) | Классы и наследование: `Driver` → `Pilot` 🏎️ |

<br>

## Структура

Всё на своих местах.

```text
olymp/
├── contests/
│   └── 2026-icpc-kyrgyzstan-qual/
│       ├── statements/      условия задач (PDF)
│       └── solutions/       решения: A.py, B.py, …
├── algorithms/
│   └── sorting/             классические алгоритмы
├── cpp-basics/              песочница по C++
└── assets/                  картинки для README
```

Новый контест — новая папка `contests/<год>-<название>/` с такими же `statements/` и `solutions/`.

<br>

## Запуск

Скопировал. Запустил. Готово.

```bash
# Python
python3 contests/2026-icpc-kyrgyzstan-qual/solutions/D.py <<< 34
# 8 15

# C++
clang++ -std=c++17 -O2 algorithms/sorting/bubble_sort_swaps.cpp -o bubble
echo "4  4 2 3 1" | ./bubble
# 5
```

<br>

<img src="assets/footer.svg" alt="Stay hungry. Stay foolish. — Steve Jobs, 1955–2011" width="100%">

<p align="center">
  <sub>Сделано с ☕ и <code>-O2</code> &nbsp;·&nbsp; <a href="https://github.com/a1tvv">@a1tvv</a></sub>
</p>
