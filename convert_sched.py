
import datetime

def read_csv(fn):
    header = None
    data = []

    f = open(fn,'r')
    while True:
        line = f.readline()
        if len(line) == 0:
            break

        line = line.rstrip('\n\r ')
        line = line.split(',')
        if not header:
            header = line
        else:
            data.append(dict(zip(header,line)))

    f.close()
    return data, header


def convert_date(line, month_map):
    d = [x.rstrip(',') for x in line]
    return "%s%02d%02d" % (d[2],month_map[d[0]],int(d[1]))

def convert_game(line, team_map):
        at = line.index('at')
        # tm, am_pm = line[-3], line[-2]

        tm = line[-2]
        if tm == 'TBD': tm = '1:00p'

        if '/' in tm:
            tm = tm.split('/')[0]

        ## format 8:30p
        am_pm = tm[-1]
        tm = tm[:-1]

        hm = tm.split(':')
        hour, mins = 0, 0
        if len(hm) == 1: 
            hour = int(hm[0])
        else:
            hour, mins = int(hm[0]), int(hm[1])

        if am_pm == 'p':
            hour = hour +12
        game_time  = (hour*100)+mins

        def clean(s):
            if s.startswith('('): return False
            if s.endswith(')'): return False
            return True

        away = " ".join(line[:at])
        home = " ".join([ x for x in line[at+1:-2] if clean(x) ])
        return team_map[home], team_map[away], game_time




teams, _  = read_csv('nfl_teams.csv')

team_map = {}
for row in teams:
    team_map[row['Team']] = row['Code']

days = "Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday,".split()

month_map = {}
for i in range(1,13):
    month = datetime.datetime(2001,i,1).strftime('%B')
    month_map[month] = i

week = None
date, time = None, None
home, away = None, None

f = open('nfl_schedule_2018.txt')
while True:
    line = f.readline()
    if len(line) == 0:
        break

    line = line.rstrip('\n\r ')
    if len(line) == 0: continue 

    line = line.replace('*','')
    line = line.split()
    if line[0] == 'Week':
        week = line[1] 
    elif line[0] in days:
        date = convert_date(line[1:],month_map)
    elif line[0] in ['TBD','Network,']:
        continue
    else:
        home, away, time = convert_game(line,team_map)
        ## week,hone,away,date,time
        print("%s,%s,%s,%s,%s,," % (week,home,away,date,time))


f.close()
