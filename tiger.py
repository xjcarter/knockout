
import shutil 

def copy(f1,f2):
    shutil.copy(f1,f2)



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

def init_scores():
    players, _ = read_csv('players.csv')
    demo_user = players[-1]['user_id']
    for f in "picks_wk8.csv picks_wk9.csv picks_wk17.csv".split():
        picks, _ = read_csv(f)
        picks[-1]['user_id'] = demo_user
        to_csv(f,picks)


def play(score_file,report=False):
    shutil.copy(score_file,'nfl_sched.csv')
    players, _ = read_csv('players.csv')
    demo_user = players[-1]['user_id']

    if report:
        stats_and_standings(send_to='DEMO ' + demo_user)

def ff_picks(picks_file):
    shutil.copy(picks_file,'picks.csv')

def demo():
    
    shutil.copy('nfl_sched.csv','nfl_sched.bkp')
    shutil.copy('picks.csv','picks.bkp')

    # 1. register
    play('nfl_sched_wk0.csv')  #2
    # 3. player picks NYG
    play('nfl_sched_wk1.csv',True)  #3
    # 5. player picks DAL
    play('nfl_sched_wk2.csv',True)  #6

    init_scores() # 7
    ff_picks('picks_wk8.csv')  # 8 
    play('nfl_sched_wk8.csv',True) 

    # 9 player picks BAL 
    play('nfl_sched_wk9.csv',True)  # 10

    ff_picks('picks_wk17.csv')  # 11
    play('nfl_sched_wk17.csv',True) 

    players, _ = read_csv('players.csv')
    ## remove demo player
    players = players[-1]
    to_csv(players)

    shutil.copy('nfl_sched.bkp','nfl_sched.csv')
    shutil.copy('picks.bkp','picks.csv')












