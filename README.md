<!-- Этот файл собирается автоматически: python3 scripts/build.py. Правки вручную перезапишутся. -->
<a href="#contests"><img src="assets/banner.svg" alt="Алтай Абдурахим — олимпиадное программирование" width="100%"></a>

<p align="center">
  <a href="#contests">Контесты&nbsp;›</a>&emsp;
  <a href="#editorials">Разборы&nbsp;›</a>&emsp;
  <a href="#algorithms">Алгоритмы&nbsp;›</a>&emsp;
  <a href="#structure">Структура&nbsp;›</a>&emsp;
  <a href="#run">Запуск&nbsp;›</a>
</p>

<br>

<img src="assets/stats.svg" alt="Решено задач: 6" width="100%">

<br>
<br>

<p align="center">
  <i>«Talk is cheap. Show me the code.»</i><br>
  <sub>— Linus Torvalds</sub>
</p>

<br>

<a name="contests"></a>
<img src="assets/titles/contests.svg" alt="Контесты" width="100%">

<a href="contests/2026-icpc-qual/statements"><img src="assets/contests/2026-icpc-qual/card.svg" alt="ICPC NERC Kyrgyzstan Qualification, 3 октября 2026" width="100%"></a>

<p>
<a href="contests/2026-icpc-qual/statements/A.pdf"><img src="assets/contests/2026-icpc-qual/A.svg" alt="A · Немного истории — Решена" width="79%"></a><a href="contests/2026-icpc-qual/solutions/A.py"><img src="assets/rows/btn-python.svg" alt="Код A" width="20%"></a><br>
<a href="contests/2026-icpc-qual/statements/B.pdf"><img src="assets/contests/2026-icpc-qual/B.svg" alt="B · Ответственная стирка — Решена" width="79%"></a><a href="contests/2026-icpc-qual/solutions/B.py"><img src="assets/rows/btn-python.svg" alt="Код B" width="20%"></a><br>
<a href="contests/2026-icpc-qual/statements/C.pdf"><img src="assets/contests/2026-icpc-qual/C.svg" alt="C · Сизифов труд — Черновик" width="79%"></a><a href="contests/2026-icpc-qual/solutions/C.py"><img src="assets/rows/btn-python.svg" alt="Код C" width="20%"></a><br>
<a href="contests/2026-icpc-qual/statements/D.pdf"><img src="assets/contests/2026-icpc-qual/D.svg" alt="D · Чат-бот на калькуляторе — Решена" width="79%"></a><a href="contests/2026-icpc-qual/solutions/D.py"><img src="assets/rows/btn-python.svg" alt="Код D" width="20%"></a><br>
<a href="contests/2026-icpc-qual/statements/E.pdf"><img src="assets/contests/2026-icpc-qual/E.svg" alt="E · Сортировка вставками — Решена" width="79%"></a><a href="contests/2026-icpc-qual/solutions/E.cpp"><img src="assets/rows/btn-cpp.svg" alt="Код E" width="20%"></a><br>
<a href="contests/2026-icpc-qual/statements/H.pdf"><img src="assets/contests/2026-icpc-qual/H.svg" alt="H · Каждому префиксу по медиане! — Скоро" width="79%"></a><a href="contests/2026-icpc-qual/statements/H.pdf"><img src="assets/rows/btn-soon.svg" alt="Скоро" width="20%"></a><br>
</p>

<br>

<a name="editorials"></a>
<img src="assets/titles/editorials.svg" alt="Разборы" width="100%">

<img src="assets/contests/2026-icpc-qual/editorials.svg" alt="A: ICPC Regional — каждый год с 2005-го; ICPC Qual — с 2019-го, кроме 2020 и 2021; School Regional и School Qual — в 2026-м; Хватает трёх условий на год B: Все носки — одна стирка; Яркие цвета и белый — каждый отдельно,; тёмные (чёрный, синий, серый) — вместе; Майки — одна стирка на цветовую группу; Кофты и штаны — ⌈k/2⌉ стирок на группу C: Позиция после k-го дня:; f(k) = k·A − B·k(k−1)/2; Растёт, пока k·B &lt; A, поэтому; максимум при k = ⌈A/B⌉ — за O(1); Осталось читать Q пар вместо одной D: Перебираем все числа от 0 до N; Обычный вид: цифры ⊆ {0,1,5,8}; Перевёрнутый: цифры ⊆ {0,1,3,5,7,8}; N ≤ 123 456 — перебор с запасом" width="100%">

<br>
<br>

<a name="algorithms"></a>
<img src="assets/titles/algorithms.svg" alt="Алгоритмы" width="100%">

<a href="algorithms/sorting/bubble_sort_swaps.cpp"><img src="assets/rows/bubble_sort_swaps.svg" alt="Сортировка пузырьком — O(n²)" width="100%"></a>
<a href="algorithms/sorting/selection_sort.cpp"><img src="assets/rows/selection_sort.svg" alt="Сортировка выбором — O(n²)" width="100%"></a>

<br>
<br>

<a name="structure"></a>
<img src="assets/titles/structure.svg" alt="Структура" width="100%">

<img src="assets/structure.svg" alt="Структура репозитория" width="100%">

<br>
<br>

<a name="run"></a>
<img src="assets/titles/run.svg" alt="Запуск" width="100%">

<img src="assets/run.svg" alt="Запуск решений в терминале" width="100%">

<details>
<summary>Скопировать команды</summary>
<br>

```bash
# Python
python3 contests/2026-icpc-qual/solutions/D.py <<< 34
# 8 15

# C++
clang++ -std=c++17 -O2 algorithms/sorting/bubble_sort_swaps.cpp -o bubble
echo "4  4 2 3 1" | ./bubble
# 5

# Пересобрать README вручную
python3 scripts/build.py
```

</details>

<br>

<img src="assets/footer.svg" alt="Stay hungry. Stay foolish. — Steve Jobs, 1955–2011" width="100%">

<p align="center">
  <sub>Сделано с ☕ и <code>-O2</code> &nbsp;·&nbsp; <a href="https://github.com/a1tvv">@a1tvv</a></sub>
</p>
