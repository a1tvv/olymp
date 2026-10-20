#include <clocale>
#include <iostream>
#include <vector>
#include <string>

using namespace std;

class Driver {
public:
    string name;
    Driver(string n) : name(n) {}
    void hello() { cout << "I'm " << name << endl; }
};

class Pilot : public Driver {
public:
    int wins;
    Pilot(string n, int w) : Driver(n) { wins = w; }
};

int main() {
    Pilot p1("Max", 60);
    p1.hello();   // ← что выведет?
    cout << p1.wins;   // ← что выведет?
    return 0;
}