// acmp №892 · Время года
// https://acmp.ru/index.asp?main=task&id_task=892
// Сложность: 10%
//
// По заданному номеру месяца в году требуется определить время года.
//
// Входные данные: входной файл INPUT.TXT содержит натуральное число N (N ≤ 100) – номер
// месяца.
//
// Выходные данные: в выходной файл OUTPUT.TXT выведите для летних месяцев значение
// «Summer», для зимних – «Winter», для весенних – «Spring», для осенних – «Autumn». Если
// число не соответствует возможному значению месяца, то в этом случае следует вывести
// «Error».
//
// Примеры:
//   3 → Spring
//   15 → Error

#include <iostream>

using namespace std;

int main() {
    int n;
    cin >> n;

    if (n == 12 or n == 1 or n == 2) {
        cout << "Winter";
    } else if (n >= 3 and n <= 5) {
        cout << "Spring";
    } else if (n >= 6 and n <= 8) {
        cout << "Summer";
    } else if (n >= 9 and n <= 11) {
        cout << "Autumn";
    } else {
        cout << "Error";
    }
}
