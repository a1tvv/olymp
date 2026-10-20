n = int(input())
a = set('0158')
b = set('013578')
c1=c2=0
for i in range(n+1):
    s = set(str(i))
    if s <=a:
        c1+=1
    if s <=b:
        c2+=1
print(c1, c2)