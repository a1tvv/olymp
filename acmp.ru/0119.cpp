// acmp №119 · Сортировка времени
// https://acmp.ru/index.asp?main=task&id_task=119
// Сложность: 23%
//
// Требуется выполнить сортировку временных моментов, заданных в часах, минутах и секундах.
//
// Входные данные: во входном файле INPUT.TXT в первой строке записано число N (1 ≤ N ≤ 100),
// а в последующих N строках N моментов времени. Каждый момент времени задается 3 целыми
// числами - часы (от 0 до 23), минуты (от 0 до 59) и секунды (от 0 до 59).
//
// Выходные данные: в выходной файл OUTPUT.TXT выведите моменты времени, упорядоченные в
// порядке неубывания без ведущих нулей.
//
// Пример (« / » — переход на новую строку):
//   4 / 10 20 30 / 7 30 00 / 23 59 59 / 13 30 30 → 7 30 0 / 10 20 30 / 13 30 30 / 23 59 59

#include <iostream>
#include <vector>

using namespace std;

void compare(vector<int>& massive) {
    for (int i=0; i<massive.size() - 1; i++) {
        for (int j=0; j<massive.size() - i - 1; j++) {
            if (massive[j] > massive[j + 1]) {
                int sort = massive[j];
                massive[j] = massive[j+1];
                massive[j+1] = sort;
            }
        }
    }
}


int main() {
    int t = 0;
    cin >> t;
    int h, m, s;
    
    vector<int> massive;
    int sum;

    for (int i=0; i<t; i++) {
        cin >> h;
        cin >> m;
        cin >> s;
        
        h = h*3600;
        m = m*60;

        sum = h+s+m;
        
        massive.push_back(sum);
    }

    compare(massive);

    for (int i = 0; i<massive.size(); i++) {
        cout << massive[i]/3600 << " " 
        << massive[i]%3600/60 << " " 
        << massive[i]%3600%60 << " "
        << endl;
    }

}