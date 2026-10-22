A = int(input())
B = int(input())

D = 0
D_max = 0

if A <= B:
    D_max = A

if A > B:
    test = True
    i = 1
    j = B
    while test:
        D += A
        B *= i
        if D_max < D:
            D_max = D
        if D < D_max:
            test = False
        D -= B
        i += 1
        B = j

print(D_max)