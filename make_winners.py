

import pandas
import random

df = pandas.read_csv('nfl_teams.csv')
codes = df['Code'].tolist()
codes = [ x.lower() for x in codes ]
j = []
for i in range(7):
    random.shuffle(codes)
    m = codes[:]
    j.append(dict(week=i+1,winners="|".join(m[:16])))

q = pandas.DataFrame(j)
q.to_csv("winners.csv",index=False)



