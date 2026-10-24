// acmp №1231 · Сортировка пузырьком
// https://acmp.ru/index.asp?main=task&id_task=1231
// Сложность: 18%
//
// Задан целочисленный массив, состоящий из N элементов. Требуется посчитать число инверсий
// (обмена значений соседних элементов массива) в процессе сортировки элементов массива по
// неубыванию при использовании алгоритма сортировки «пузырьком» (BubbleSort).
//
// Входные данные: первая строка входного файла INPUT.TXT содержит натуральное число N –
// количество элементов в массиве (N ≤ 1000). Во второй строке содержатся N целых чисел, не
// превосходящих 10^9 по абсолютной величине.
//
// Выходные данные: в выходной файл OUTPUT.TXT выведите целое число – количество инверсий в
// процессе сортировки методом «пузырька».
//
// Примеры (« / » — переход на новую строку):
//   3 / 7 2 5 → 2
//   10 / 12 7 92 5 18 4 32 48 11 74 → 18

#include <iostream>
#include <vector>

using namespace std;

long long bubbleSort(vector<long long>& arr) {
    long long count = 0;

    for (int i = 0; i < arr.size() - 1; i++) {
         for (int j =0; j < arr.size() - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                long long temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
                count++;
            }
        }
    }

    return count;
}

int main() {
    int n;
    cin>> n;
    vector<long long> arr(n);
    for (int i =0; i<n; i++) {
        cin >> arr[i];
    }

    long long result = bubbleSort(arr);
    cout<< result << endl;

    return 0;
}