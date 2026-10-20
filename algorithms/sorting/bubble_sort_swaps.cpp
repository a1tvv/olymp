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