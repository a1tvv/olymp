#include <iostream>

using namespace std;

int main () {
    long long n, k;
    cin >> n >> k;

    cout << k+1 << " ";
    for (int i = 0; i < n; i++) {
        if (i+1 != k+1){
            cout << i+1 << " ";
        }
    }

}