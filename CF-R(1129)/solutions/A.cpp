#include <iostream>
#include <vector>

using namespace std;

int main() {
    int t,k,n,x,v;

    cin >> t;
    for (int i=0; i<t; i++) {
        cin >> n;
        cin >> k;

        vector<int> a;
        for (int i=0; i<n; i++) {
            cin >> x;
            a.push_back(x);
        }

        for (int v=0; v<=n; v++) {
            int est = 0;
            int mal = 0;

            for (int j=0; j<a.size(); j++) {
                if (a[j] == v) {
                    est++;
                }
                if (a[j] <= v) {
                    mal++;
                }
            }

            if (est == 0 or mal < (v + 1)*k) {
                cout << v << "\n";
                break;
            }
        }
    }

}