#include <iostream>
#include <vector>

using namespace std;

int main() {
    long long n, k;
    cin >> n >> k;

    vector<long long> result;
    long long m = n;
    while (m > 0 && k >= m - 1) {
        result.push_back(m);
        k -= m - 1;
        m--;
    }
    if (m > 0) {
        result.push_back(k + 1);
        for (long long x = 1; x <= m; x++) {
            if (x != k + 1) {
                result.push_back(x);
            }
        }
    }

    for (int i = 0; i < result.size(); i++) {
        cout << result[i] << " ";
    }
    cout << endl;

    return 0;
}
