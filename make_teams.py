

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

data, _ = read_csv('nfl_teams.csv')

j = []
for v in data:
    code = v['Code']
    team = v['Team']
    ##print("<input id='%s' type='submit' name='%s' value='%s' onclick='pick_team()'>" % (code,code,team))
    j.append(v['Code'])

print("|".join(j))
   



