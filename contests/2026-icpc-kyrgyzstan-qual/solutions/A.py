k = int(input())

competitions = []
competitions.append('ICPC Regional')

if  k >= 2019 and k != 2020 and k != 2021:
    competitions.append('ICPC Qual')

if k == 2026:
    competitions += ['School Regional', 'School Qual']

print(len(competitions))
for competition in competitions:
    print(competition)