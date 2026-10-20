#include <iostream>
#include <clocale> 
#include <string>

using namespace std;

void print(string word) {
    cout << word << endl;
}

int main() {
    setlocale(LC_ALL, "RU");

    print("Салам по пополам, какой пароль? ");

    return 0;
}
