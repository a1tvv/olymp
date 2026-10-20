<a href="#contests"><img src="assets/banner.svg" alt="Алтай Абдурахим — олимпиадное программирование" width="100%"></a>

<p align="center">
  <a href="#contests">Контесты&nbsp;›</a>&emsp;
  <a href="#editorials">Разборы&nbsp;›</a>&emsp;
  <a href="#algorithms">Алгоритмы&nbsp;›</a>&emsp;
  <a href="#structure">Структура&nbsp;›</a>&emsp;
  <a href="#run">Запуск&nbsp;›</a>
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

<a name="contests"></a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/titles/contests-dark.svg">
  <img src="assets/titles/contests-light.svg" alt="Контесты" width="100%">
</picture>

<a href="contests/2026-icpc-kyrgyzstan-qual/statements"><img src="assets/icpc-kg-qual-2026.svg" alt="ICPC NERC Kyrgyzstan Qualification, 3 октября 2026: A, B, D решены; C — черновик; E, H — скоро" width="100%"></a>

<p>
<a href="contests/2026-icpc-kyrgyzstan-qual/statements/A.pdf"><img src="assets/rows/A.svg" alt="A · Немного истории" width="79%"></a><a href="contests/2026-icpc-kyrgyzstan-qual/solutions/A.py"><img src="assets/rows/btn-python.svg" alt="Код A на Python" width="20%"></a><br>
<a href="contests/2026-icpc-kyrgyzstan-qual/statements/B.pdf"><img src="assets/rows/B.svg" alt="B · Ответственная стирка" width="79%"></a><a href="contests/2026-icpc-kyrgyzstan-qual/solutions/B.py"><img src="assets/rows/btn-python.svg" alt="Код B на Python" width="20%"></a><br>
<a href="contests/2026-icpc-kyrgyzstan-qual/statements/C.pdf"><img src="assets/rows/C.svg" alt="C · Сизифов труд" width="79%"></a><a href="contests/2026-icpc-kyrgyzstan-qual/solutions/C.py"><img src="assets/rows/btn-python.svg" alt="Код C на Python" width="20%"></a><br>
<a href="contests/2026-icpc-kyrgyzstan-qual/statements/D.pdf"><img src="assets/rows/D.svg" alt="D · Чат-бот на калькуляторе" width="79%"></a><a href="contests/2026-icpc-kyrgyzstan-qual/solutions/D.py"><img src="assets/rows/btn-python.svg" alt="Код D на Python" width="20%"></a><br>
<a href="contests/2026-icpc-kyrgyzstan-qual/statements/E.pdf"><img src="assets/rows/E.svg" alt="E · Сортировка вставками" width="79%"></a><a href="contests/2026-icpc-kyrgyzstan-qual/statements/E.pdf"><img src="assets/rows/btn-soon.svg" alt="Скоро" width="20%"></a><br>
<a href="contests/2026-icpc-kyrgyzstan-qual/statements/H.pdf"><img src="assets/rows/H.svg" alt="H · Каждому префиксу по медиане!" width="79%"></a><a href="contests/2026-icpc-kyrgyzstan-qual/statements/H.pdf"><img src="assets/rows/btn-soon.svg" alt="Скоро" width="20%"></a><br>
</p>

<br>

<a name="editorials"></a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/titles/editorials-dark.svg">
  <img src="assets/titles/editorials-light.svg" alt="Разборы" width="100%">
</picture>

<img src="assets/editorials.svg" alt="Разборы: A — три условия на год, O(1). B — носки одной стиркой, майки по цветовым группам, кофты и штаны по ⌈k/2⌉, O(N). C — максимум f(k) = kA − B·k(k−1)/2 при k = ⌈A/B⌉ (черновик). D — перебор чисел от 0 до N, O(N log N)." width="100%">

<br>
<br>

<a name="algorithms"></a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/titles/algorithms-dark.svg">
  <img src="assets/titles/algorithms-light.svg" alt="Алгоритмы" width="100%">
</picture>

<a href="algorithms/sorting/bubble_sort_swaps.cpp"><img src="assets/rows/bubble-sort.svg" alt="Сортировка пузырьком — считает число обменов, O(n²), C++" width="100%"></a>

<br>
<br>

<a name="cpp"></a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/titles/cpp-dark.svg">
  <img src="assets/titles/cpp-light.svg" alt="C++ basics" width="100%">
</picture>

<a href="cpp-basics/hello.cpp"><img src="assets/rows/hello-cpp.svg" alt="hello.cpp — первая программа" width="100%"></a>
<a href="cpp-basics/f1.cpp"><img src="assets/rows/f1-cpp.svg" alt="f1.cpp — классы и наследование" width="100%"></a>

<br>
<br>

<a name="structure"></a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/titles/structure-dark.svg">
  <img src="assets/titles/structure-light.svg" alt="Структура" width="100%">
</picture>

<img src="assets/structure.svg" alt="Структура: contests/ — условия и решения контестов, algorithms/ — классические алгоритмы, cpp-basics/ — песочница по C++, assets/ — картинки для README" width="100%">

<br>
<br>

<a name="run"></a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/titles/run-dark.svg">
  <img src="assets/titles/run-light.svg" alt="Запуск" width="100%">
</picture>

<img src="assets/run.svg" alt="Запуск решений в терминале" width="100%">

<details>
<summary>Скопировать команды</summary>
<br>

```bash
# Python
python3 contests/2026-icpc-kyrgyzstan-qual/solutions/D.py <<< 34
# 8 15

# C++
clang++ -std=c++17 -O2 algorithms/sorting/bubble_sort_swaps.cpp -o bubble
echo "4  4 2 3 1" | ./bubble
# 5
```

</details>

<br>

<img src="assets/footer.svg" alt="Stay hungry. Stay foolish. — Steve Jobs, 1955–2011" width="100%">

<p align="center">
  <sub>Сделано с ☕ и <code>-O2</code> &nbsp;·&nbsp; <a href="https://github.com/a1tvv">@a1tvv</a></sub>
</p>
