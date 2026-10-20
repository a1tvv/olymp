<p align="center">
  <img src="assets/banner.svg" alt="olymp — олимпиадное программирование" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3">
  <img src="https://img.shields.io/badge/C%2B%2B-17-00599C?style=for-the-badge&logo=cplusplus&logoColor=white&labelColor=0d1117" alt="C++17">
  <img src="https://img.shields.io/badge/ICPC-NERC_2026-a78bfa?style=for-the-badge&labelColor=0d1117" alt="ICPC NERC 2026">
  <img src="https://img.shields.io/badge/%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%BE-3%2F6-22c55e?style=for-the-badge&labelColor=0d1117" alt="решено 3 из 6">
</p>

<p align="center">
  <i>«Talk is cheap. Show me the code.»</i><br>
  <sub>— Linus Torvalds</sub>
</p>

<p align="center">
  <a href="#-контесты"><b>Контесты</b></a> &nbsp;·&nbsp;
  <a href="#-алгоритмы"><b>Алгоритмы</b></a> &nbsp;·&nbsp;
  <a href="#-c-basics"><b>C++ basics</b></a> &nbsp;·&nbsp;
  <a href="#-структура"><b>Структура</b></a> &nbsp;·&nbsp;
  <a href="#-запуск"><b>Запуск</b></a>
</p>

<br>

## 🏆 Контесты

### ICPC NERC · Kyrgyzstan Qualification Contest 2026

<sup>📅 3 октября 2026 &nbsp;·&nbsp; 📍 Кыргызстан &nbsp;·&nbsp; 🧮 6 задач &nbsp;·&nbsp; ✅ решено 3</sup>

| | Задача | Темы | Решение | Статус |
|:-:|:--|:--|:-:|:-:|
| <kbd>A</kbd> | [Немного истории](contests/2026-icpc-kyrgyzstan-qual/statements/A.pdf) | `реализация` | [Python](contests/2026-icpc-kyrgyzstan-qual/solutions/A.py) | ✅ |
| <kbd>B</kbd> | [Ответственная стирка](contests/2026-icpc-kyrgyzstan-qual/statements/B.pdf) | `жадность` `группировка` | [Python](contests/2026-icpc-kyrgyzstan-qual/solutions/B.py) | ✅ |
| <kbd>C</kbd> | [Сизифов труд](contests/2026-icpc-kyrgyzstan-qual/statements/C.pdf) | `математика` | [Python](contests/2026-icpc-kyrgyzstan-qual/solutions/C.py) | 🚧 |
| <kbd>D</kbd> | [Чат-бот на калькуляторе](contests/2026-icpc-kyrgyzstan-qual/statements/D.pdf) | `перебор` `цифры` | [Python](contests/2026-icpc-kyrgyzstan-qual/solutions/D.py) | ✅ |
| <kbd>E</kbd> | [Сортировка вставками](contests/2026-icpc-kyrgyzstan-qual/statements/E.pdf) | `конструктив` `инверсии` | — | ⏳ |
| <kbd>H</kbd> | [Каждому префиксу по медиане!](contests/2026-icpc-kyrgyzstan-qual/statements/H.pdf) | `медиана` `кучи` | — | ⏳ |

> [!NOTE]
> ✅ проходит все примеры из условия &nbsp;·&nbsp; 🚧 черновик &nbsp;·&nbsp; ⏳ в планах
>
> Название задачи ведёт на условие в PDF.

#### Разборы

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

## 🧠 Алгоритмы

| Алгоритм | Что делает | Сложность | Код |
|:--|:--|:-:|:-:|
| Сортировка пузырьком | Сортирует массив и считает число обменов — оно равно числу инверсий | `O(n²)` | [C++](algorithms/sorting/bubble_sort_swaps.cpp) |

<br>

## 🧩 C++ basics

Песочница, в которой разбираю основы языка.

| Файл | О чём |
|:--|:--|
| [`hello.cpp`](cpp-basics/hello.cpp) | Первая программа: функция, вывод, `setlocale` |
| [`f1.cpp`](cpp-basics/f1.cpp) | Классы и наследование: `Driver` → `Pilot` 🏎️ |

<br>

## 📁 Структура

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

## 🚀 Запуск

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

<p align="center">
  <sub>Сделано с ☕ и <code>-O2</code> &nbsp;·&nbsp; <a href="https://github.com/a1tvv">@a1tvv</a></sub>
</p>
