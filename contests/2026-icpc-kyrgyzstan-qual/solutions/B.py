import sys
d = sys.stdin.read().split()
s = 0
tg = set()
og = {}
for i in range(int(d[0])):
    c, t = d[1+2*i], d[2+2*i]
    g = c if c in ('Yellow', 'Green', 'Red', 'White') else 'Dark'
    if t == 'Socks': s = 1
    elif t == 'T-shirt': tg.add(g)
    else: og[g] = og.get(g, 0) + 1

print(s + len(tg) + sum((v+1) // 2 for v in og.values()))