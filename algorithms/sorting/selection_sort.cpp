#include <iostream>
#include <vector>

using namespace std;

vector<int> selectionSort(vector<long long>& arr) {
    vector<int> result;

    for (int end = arr.size() - 1; end >= 0; end--) {
        int max_idx = 0;
        for (int j = 1; j <= end; j++) {
            if (arr[j] > arr[max_idx]) {
                max_idx = j;
            }
        }
        result.push_back(max_idx);
        swap(arr[max_idx], arr[end]);
    }

    return result;
}

int main() {
    int n;
    cin >> n;
    vector<long long> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }

    vector<int> result = selectionSort(arr);
    for (int i = 0; i < result.size(); i++) {
        cout << result[i] << " ";
    }
    cout << endl;

    return 0;
}
