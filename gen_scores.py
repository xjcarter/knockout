
from random import randrange
import sys 

def read_csv(fn):
    header = None
    data = []

    f = open(fn,'r')
    while True:
        line = f.readline()
        if len(line) == 0:
            break

        line = line.rstrip('\n\r ')
        if len(line) == 0: continue
        line = line.split(',')
        if not header:
            header = line
        else:
            data.append(dict(zip(header,line)))

    f.close()
    return data, header

def write_csv(data,header,fn):
    ## rewrite and update current file 
    with open(fn,'w') as f:
        f.write('%s\n' % (",".join(header)))
        for row in data:
            line = []
            for col in header:
                line.append("%s" % row[col])
            f.write('%s\n' % (",".join(line)))


last = int(sys.argv[1]) + 1
populate = list(range(1,last)) 

nfl_sched, header = read_csv('nfl_sched.csv')
for row in nfl_sched:
    week = int(row['week'])
    if week in populate:
        if row['score_home'] == '':
            home = away = 0
            while home == away:
                home, away = randrange(50), randrange(50)
            row['score_home'] = home
            row['score_away'] = away

write_csv(nfl_sched, header, "nfl_sched.csv")







