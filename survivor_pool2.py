
import os
from flask import *
import re
import pprint
import datetime
import mail_client




app = Flask(__name__)
app.debug = True

##current week is the week of upcoming games 
mulligans = 1

##user_id = 'jenlo' 
global_user_id = 'xjcarter' 


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


def to_csv(filename,data,header=None):
    if len(data) > 0:
        if header is None:
            header = data[0].keys()
        with open(filename,'w') as f:
            f.write(",".join(header) + "\n")
            for d in data:
                line = [str(d[k]) for k in header ]
                f.write(",".join(line) + "\n")


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

    status = 'DEAD'
    if falls <= mulligans: status = 'ALIVE'

    actives = len(survivors)
    ## end of game
    if current_week == 18:
        ## if you are perfect - definite winner
        if status == 'ALIVE' and p['falls'] == 0: status = 'WINNER'
        if status == 'ALIVE' and p['falls'] == 1:
            ## perfect records exist = eliminated 
            if perfects > 0:
                status = 'DEAD'
            else:
                ## if noone is perfect = winner
                status = 'WINNER'
    else:
        ## last man standing = winner
        if actives == 1 and status == 'ALIVE': status = 'WINNER'
        ## player played thru last week and eveyone got knocked out
        if len(p['used_path']) == len(scoreboard) and actives == 0:
            status = 'WINNER'

    return dict(falls=falls, 
            used_path=used_path, 
            win_loss_path=win_loss_path, 
            scores=scores,
            current_pick=current_pick)

  


def check_kickoff(current_week,nfl_sched):

    teams = "ARI|ATL|BAL|BUF|CAR|CHI|CIN|CLE|DAL|DEN|DET|GB|HOU|IND|JAX|"
    teams += "KC|MIA|MIN|NE|NO|NYG|NYJ|OAK|PHI|PIT|LAC|SF|SEA|LAR|TB|TEN|WAS"
    teams = teams.split("|")

    ## schedule file week,home,away,date,time
    ## example 1,pit,den,20180915,1300

    kickoff_times = []
    teams_playing = [] 

    for game in nfl_sched:
        if int(game['week']) == current_week:
            home = game['home'].upper()
            away = game['away'].upper()
            kt = "%s,%s" % (game['date'],game['time'])
            teams_playing.append(home)
            teams_playing.append(away)
            kickoff_times.append("%s,%s" % (home,kt))
            kickoff_times.append("%s,%s" % (away,kt))

    byes = [ x for x in teams if x not in teams_playing]

    return byes, kickoff_times



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




@app.route("/show_ladder",methods=['GET','POST'])
def show_ladder(*args,**kwargs):
    global global_user_id
    global mulligans 

    ## gloabl_user_id for testing show_ladder directly...
    user_id = global_user_id
    try:
        user_id = kwargs['user_id']
    except KeyError:
        pass

    ## table of players and weekly team selection
    ## player,picks
    ## xjcarter,ari|dal|lac|pit|phi|den|oak
    ## - in the above example xjcarter has mad pick up to week 3... 
    picks, picks_header  = read_csv('picks.csv')
    players, _ = read_csv('players.csv')

    ## table of winning teams for the week
    ## week,temms 
    ## 1, chi|hou|dal|...|pit
    ## winners, _ = read_csv('winners.csv')
    ## print("winners_size=",len(winners))

    ## mapping of nfl teams and city code
    ## Team,Code,Division
    ## Arizona Cardinals,ARI,NFC West
    teams_nfl, _ = read_csv('nfl_teams.csv') 
    nfl_teams = {}
    for team_row in teams_nfl:
        nfl_teams[team_row['Code']] = team_row['Team']

    nfl_sched, _ = read_csv('nfl_sched.csv')
    scoreboard = parse_schedule(nfl_sched)

    ## iterate over eevery player in the game
    ## player,picks
    ## xjcarter,ari|dal|lac|pit|phi|den|oak
    survivors = [] 
    perfects = 0
    pick_map = {}

    for row in picks:
        player, teams = row['player'], row['picks']
        pick_map[player] = []
        teams_played = []
        if len(teams) > 0:
            teams_played = [x.upper() for x in teams.split("|")]

        vitals = parse_path(teams_played,scoreboard)
        pick_map[player] = dict(vitals)
        falls = vitals['falls']
        if falls <= mulligans:
            if falls == 0: perfects += 1
            survivors.append(player)


    ## string holding survivors/totalplayers
    tally_str = '%d|%d' % (len(survivors),len(players))

    ## fill the players picks in the html array
    ## if no a survivor (they will have two red colored entries)
    ## post "ELIMINATED." at the bottom of thier list'
    ## diasble all selctions 

    ## otherwise handle survivors

    p = pick_map[user_id] 

    current_week = len(scoreboard)+1
    byes, kickoff_times = check_kickoff(current_week,nfl_sched)


    ## post entry to logfile         
    tstamp = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
    log_entry = "%s: %10s %s [%s] %02d %s\n" % (tstamp,user_id,"|".join(p['used_path']),p['current_pick'],current_week,status)
    with open('picks.log','a') as f:
        f.write(log_entry)


    print("user_id= ",user_id)
    print("current_pick=",p['current_pick'])
    print("used_path=",p['used_path'])
    print("win_loss_path=",p['win_loss_path'])
    print("kickoff_times=",kickoff_times)
    print("byes=",byes)
    print("status=",status)
    print(tally_str)


    return render_template('knockout.html', 
                            current_user=user_id,
                            current_pick=p['current_pick'],
                            used_path="|".join(p['used_path']),
                            scores="|".join(p['scores']),
                            win_loss_path="|".join(p['win_loss_path']),
                            tally_str=tally_str, 
                            kickoff_times="|".join(kickoff_times),
                            byes="|".join(byes),
                            status=p['status'])



@app.route("/save_ladder", methods=['POST'])
def save_ladder(*args,**kwargs):
    ##pprint.pprint(request.environ, depth=5)

    ## remember these are accessed iv html element **NAME**
    ## an NOT id.

    log_entry = ''

    current_user = request.form['current_user']
    print ("current_user= " + current_user)
    used_path = request.form['used_path']
    print ("used_path= " + used_path)
    current_pick = request.form['current_pick']
    print ("current_pick= " + current_pick)

    ## read current pcik file
    picks, picks_header  = read_csv('picks.csv')
    pick_map = {}
    for row in picks:
        player, teams_played = row['player'], row['picks']
        if player != current_user:
            pick_map[player] = teams_played
        else:
            if len(used_path) > 0:
                pick_map[player] = used_path + "|" + current_pick
            else:
                pick_map[player] = current_pick
            tstamp = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
            log_entry = "%s: %10s %s [%s]" % (tstamp,player,used_path,current_pick)

    ## rewrite and update current file 
    with open('picks.csv','w') as f:
        f.write('%s\n' % (",".join(picks_header)))
        for k in pick_map.keys():
            line = "%s,%s\n" % (k,pick_map[k])
            f.write(line)

    ## post entry to logfile         
    with open('picks.log','a') as f:
        f.write('%s\n' % log_entry)

    ## return empty response
    return ('', 204)



###
##### LOGIN AND REGISTRATION ############
###


@app.route("/show_login")
def show_login(*args,**kwargs):
    return render_template("knockout_login.html",msg='')

@app.route("/")
def index(*args,**kwargs):
    return show_login()


@app.route("/login", methods=['POST'])
def login(*args,**kwargs):

    ##user_id,name,email,num_of_boxes,passwd,pool_id
    players_data, _  = read_csv('players.csv')
    user_id = request.form['userid']
    passwd = request.form['passwd']

    # if user_id in players_data['user_id'].tolist():
    if user_id in [x['user_id'] for x in players_data ]:
        pdf = [x for x in players_data if x['user_id'] == user_id ]
        valid_pwd = (passwd in [ x['passwd'] for x in pdf ])
        if valid_pwd:
            return show_ladder(user_id=user_id) 
        else:
            error = r'Invalid Login.|Please Check Password.'
            return render_template('knockout_login.html', msg=error)
    else:
        error = r"Unknown UserId.|'" + user_id + r"'|Has Not Been Registered"
        return render_template('knockout_login.html', msg=error)

###
### registration validation
###

def validated(name,email,phone,user_id,passwd,confirm,players_data):

    email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    name_regex = re.compile(r"^([a-zA-Z]{2,}\s[a-zA-z]{1,}'?-?[a-zA-Z]{2,}\s?([a-zA-Z]{1,})?)$")
    userid_regex = re.compile(r"([a-zA-Z0-9_]+$)")
    phone_regex = re.compile(r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})")

    if not name_regex.match(name):
        return r"Invalid Name.|Please Enter First and Last Name"
    if not email_regex.match(email):
        return r"Invalid Email.|Please Valid Email Address"
    if not phone_regex.match(phone):
        return r"Invalid Phone Number Format.|Please Include Area Code and Number"
    if not userid_regex.match(user_id):
        return r"Invalid UserId.|Userid Contains Letters and Numbers Only"
    if len(user_id) < 6:
        return r"Invalid UserId.|Userid Must Be At Least 6 Characters."
    if  "," in passwd:
        return r"Invalid Password.|Password Contains Commas"
    if len(passwd) < 6:
        return r"Invalid Password.|Password Must Be At Least 6 Characters."
    if passwd != confirm:
        return r"Invalid Password.|Password and Confirm Do Not Match."

    userids = [ x['user_id'].lower() for x in players_data ]
    if user_id.lower() in userids:
        return r'Invalid UserId.|'+user_id+ r' Has Already Been Registered'

    return None

def email_me(new_user):

    rules = """
    <html>
    <head>
    </head>
    <body>
    <div class="rules_div">
    <div class="rule_header"><p>Rules of the Game:</p></div>
    <div class="rules">
    <ol>
    <li>Players must select one NFL team to win in the current week's NFL games.<br><br>
    During the period of picking a team to win each week, YOU CAN ONLY USE A EACH NFL TEAM ONCE</li><br>
    <li>If your selected team WINS in the current week - you SURVIVED the week's challenge and now advance to the next week of competition.</li><br>
    <li>If your selected team LOSES in the current week - you are ELIMINATED from competition. &nbsp;GAME OVER.<br><br> Only players that continue to successfully pick a winning team each week advance to the next round.</li><br>
    <li>THE MULLIGAN: &nbsp;Each player is permitted one second chance attempt ('A Mulligan') to remain in the pool upon thier inital losing pick.<br>If effect, each player is allowed to continue to play if they failed on ONE pick.  &nbsp;Once they lose again - they are completely eliminated.</li><br>
    <li>The last player to continue to advance each week WINS THE ENTIRE POOL.<br>In the case of mulitple winners (i.e. everyone left get's knocked out of the pool at the same time), the pool is divided equally among the last remaining participants.</li><br>
    <li>When the game ends - ppriority goes to winning players that DID NOT use their second chance entry ('Mulligan').<br> If winners have picked perfectly - WINNINGS ARE DIVIDED AMONG THOSE PLAYERS ONLY.<br><br>Otherwise, all ending survivors divide the total price.</li>
    </ol>
    </div>
    </div>
    </body>
    </html>
    """

    ## email me about the new user
    subject = 'KnockOut Pool: New Player: %s' % new_user['name']
    msg = "New Player\n-------------------------------------------\n"
    msg += "Name:     %s\n" % new_user['name']
    msg += "User_Id:  %s\n" % new_user['user_id']
    msg += "Email:    %s\n" % new_user['email']

    mail_client.mail("xjcarter@gmail.com",subject,msg)

    ## welcome the new user
    ## along with game rukes
    welcome = "Welcome %s (%s), to Mulligan's KnockOut Pool!\n" % (new_user['name'],new_user['user_id'])
    welcome += "\nGood Luck!\n"

    subject = "Welcome to Mulligan's KnockOut Pool"
    mail_client.mail(new_user['email'],subject,text=welcome,html=rules)


@app.route("/show_register")
def show_register(*args,**kwargs):
    info = r'Provide Contact Details|And Create a UserId and Password.'
    return render_template("knockout_register.html",msg=info)


@app.route("/register", methods=['POST'])
def register(*args,**kwargs):
    name = request.form['fullname']
    email = request.form['email']
    phone = request.form['phone']
    user_id= request.form['userid']
    passwd = request.form['passwd']
    confirm= request.form['confirm']

    players_data, header = read_csv('players.csv')

    error = validated(name,email,phone,user_id,passwd,confirm,players_data)
    if error == None:
        new_user=dict(user_id=user_id,
                      name=name,
                      email=email,
                      phone=phone,
                      passwd=passwd)

        if len(players_data) == 0:
            players_data = [new_user]
        else:
            players_data.append(new_user)

        to_csv('players.csv',players_data)

        ## add new player to the picks file as well
        picks, _ = read_csv('picks.csv')
        picks.append(dict(player=new_user['user_id'],picks=''))
        to_csv('picks.csv',picks)


        email_me(new_user)

        ## take them back to login page
        return render_template('knockout_login.html', msg= "'" + user_id + "'|Registration Complete.")
    else:
        return render_template('knockout_register.html', msg=error)


def game_report(*args,**kwargs):
    global mulligans 

    players_data, _  = read_csv('players.csv')

    picks, picks_header  = read_csv('picks.csv')
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

    return rpt


@app.route("/report")
def email_report(*args,**kwargs):
    #output number of survivors, mulligans taken, perfect players
    rpt = game_report()
    return render_template("knockout_report.html",report=rpt.replace("\n","|"))
    ## return empty response
    ## return ('', 204)

if __name__ == "__main__":
    app.run(debug=True)







