
mulligans = 1

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



def parse_path(path,scoreboard):
    global mulligans
    falls = 0
    used_path = []
    win_loss_path = []
    scores= []

    ## creates a list of dicts denoting activity for each week
    ## i.e. scoreboard struct for week3 (@ list index=2) ... 
    ## scoreboard[2][PHI] = 'Finakl Score: PHI 30, WAS 10'
    ## scoreboard[2][WAS] = 'Finakl Score: PHI 30, WAS 10'
    ## scoreboard[2][winners] = "NE|DET|...|PHI|DET|PIT|....''

    current_week = len(scoreboard)+1
    if len(path) > current_week:
        path = path[:current_week]

    for j, row in enumerate(scoreboard):
        winners= row['winners']
        try:
            team = path[j].upper()
            used_path.append(team)
            if team != 'XXX':
                scores.append("- " + row[team])
            else:
                scores.append("")
                
            if team in [winner.upper() for winner in winners]:
                win_loss_path.append('W')
            else:
                win_loss_path.append('L')
                falls += 1
        except IndexError:
            if falls <= mulligans:
                used_path.append('XXX')
                win_loss_path.append('L')
                scores.append("")
                falls += 1

    current_pick = ''
    if falls <= mulligans and len(path) == current_week:
        current_pick = path[-1]

    return dict(falls=falls, 
            used_path=used_path, 
            win_loss_path=win_loss_path, 
            scores=scores,
            current_pick=current_pick)

  

## nfl_schedule csv looks like:
## week,home,away,date,time,score_home,score_away
## 1,PIT,DAL,20180101,1300,27,13

def parse_schedule(nfl_sched):
    scoreboard = []
    for _ in range(17):
        scoreboard.append(dict())

    for row in nfl_sched:
        week = int(row['week'])
        home, away = row['home'], row['away']
        hpts, vpts = row['score_home'], row['score_away']

        ## game hasn't been played yet
        if hpts == '': break

        hpts, vpts = int(hpts), int(vpts)
        box_score = '%s %d, %s %d' % (away,vpts,home,hpts)

        ## NOTE: in the case of a tie HOME is the victor
        victor = home
        if vpts > hpts: 
            victor = away

        scb = scoreboard[week-1]
        if len(scb) == 0: scb['winners'] = []
        scb[home] = box_score
        scb[away] = box_score
        scb['winners'].append(victor)

    ##truncate socorebarod to hold only valid info
    scoreboard = [w for w in scoreboard if len(w) > 0] 

    ## creates a list of dicts denoting activity for each week
    ## i.e. scoreboard struct for week3 (@ list index=2) ... 
    ## scoreboard[2][PHI] = 'Finakl Score: PHI 30, WAS 10'
    ## scoreboard[2][WAS] = 'Finakl Score: PHI 30, WAS 10'
    ## scoreboard[2][winners] = "NE|DET|...|PHI|DET|PIT|....''

    return scoreboard

def game_report(*args,**kwargs):
    global mulligans 


    ## table of players and weekly team selection
    ## player,picks
    ## xjcarter,ari|dal|lac|pit|phi|den|oak
    ## - in the above example xjcarter has mad pick up to week 3... 
    picks, picks_header  = read_csv('picks.csv')

    ## mapping of nfl teams and city code
    ## Team,Code,Division
    ## Arizona Cardinals,ARI,NFC West
    teams_nfl, _ = read_csv('nfl_teams.csv') 
    nfl_teams = {}
    for team_row in teams_nfl:
        nfl_teams[team_row['Code']] = team_row['Team']

    nfl_sched, _ = read_csv('nfl_sched.csv')
    scoreboard = parse_schedule(nfl_sched)
    last_week = len(scoreboard)
    freq = {}

    used_mulligan = 0
    perfect = 0
    knocked_out = 0

    for row in picks:
        player, teams = row['player'], row['picks']
        teams_played = []
        if len(teams) > 0:
            teams_played = [x.upper() for x in teams.split("|")]
            for i in range(last_week):
                if i < len(teams_played):
                    team = teams_played[i]
                    try:
                        freq[team] += 1
                    except KeyError:
                        freq[team] = 1

        vitals = parse_path(teams_played,scoreboard)
        falls = vitals['falls']
        if falls <= mulligans:
            if falls == mulligans:
                used_mulligan += 1
            else:
                perfect += 1
        else:
            knocked_out += 1

    players = len(picks)
    rpt = ''
    rpt += "\n\n%25s\n" %  ("... WEEK " + str(last_week) + " REPORT")
    rpt += "\n%25s  %6s\n"  % ("Player Stats","Count")
    rpt += "%25s  %6d\n" % ("Players",players)
    rpt += "%25s  %6d\n" % ("Eliminated",knocked_out)
    rpt += "%25s  %6d\n" % ("Survivors",players - knocked_out)
    rpt += "%25s  %6d\n" % ("Perfects",perfect)
    rpt += "%25s  %6d\n" % ("Used Muliigans",used_mulligan)

    rpt += "\n\n"
    rpt += "%25s  %6s\n\n" % ("Teams Used","Count")
    for k in freq:
        if k != 'XXX':
            rpt += "%25s  %6d  (%2d%%)\n" % (nfl_teams[k],freq[k],100*freq[k]/float(players)) 

    print(rpt)

if __name__ == "__main__":
    game_report()



