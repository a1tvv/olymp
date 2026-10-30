// acmp №100 · Счастливые билеты
// https://acmp.ru/index.asp?main=task&id_task=100
// Сложность: 68%
// Черновик
//
// Требуется вычислить количество N-значных счастливых билетов. Напомним, что билет
// называется счастливым, если сумма первой половины его цифр равна сумме другой его
// половины. Например, билет 064109 счастливый, т.к. 0+6+4=1+0+9.
//
// Входные данные: в единственной строке входного файла INPUT.TXT записано натуральное
// четное число N (N ≤ 100) – количество цифр в билете.
//
// Выходные данные: в единственную строку выходного файла OUTPUT.TXT нужно вывести одно
// целое число – количество N-значных счастливых билетов.
//
// Примеры:
//   4 → 670
//   6 → 55252
//   12 → 39581170420

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;

string add(string a, string b) {
    string result = "";

    int i = a.length() -1;
    int j = b.length() -1;

    int carry = 0;

    while (i>=0 or j>=0 or carry > 0) {
        int sum = carry;

        if (i >=0) {
            sum += a[i] - '0';
            i--;
        }

        if (j >=0) {
            sum += b[j] - '0';
            j--;
        }

        carry = sum/10;
        result.push_back((sum%10) + '0');
    }
    reverse(result.begin(), result.end());
    return result;
}

int main() {
    int n;
    cin >> n;

    int h = n / 2;
    int max_sum = 9 * n;

    // ways[s] — сколько способов получить сумму цифр s
    vector<string> ways(max_sum+1, "0");
    ways[0] = "1";    // ноль цифр: сумма 0 одним способом

    // добавляем цифры по одной
    for (int digits=1; digits<=n; digits++) {
        vector<string> next(max_sum+1, "0");

        for (int s=0; s<=max_sum; s++) {
            for (int d=0; d<=9; d++) {
                if (s-d >= 0) {
                    next[s] = add(next[s], ways[s-d]);
                }
            }
        }

        ways = next;
    }

    cout << ways[9 * h];
}
