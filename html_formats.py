
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

survivor_table = """
<html>
<head>
</head>
<body>
    <table id='standings'>
      <tr id ='heading'>
        <th id='head_user'>Participant</th>
        <th class='round_header'>Count</th>
      </tr>
      <tr>
        <td class='user_id'>Players</td>
        <td class='num'>{player_count}</td>
      </tr>
    </table>
<body>
</html>
"""

css="""
<style>
    #standings
    {
        position: absolute;
        background-color: #4080bf;
        color: white;
        font-family: "Courier New";
        font-size: 18px; 
        width: 1025px;
        top: 50px;
        left: 10px;
        background: #4B79A1;  

    }

    #heading
    {
        color: white;
        font-family: "Verdana";
        font-size: 18px;
        background: #4B79A1;  
    }


    #head_user
    {
       width: 200px;
       text-align: left; 
    }

    .round_header
    {
       width: 100px;
       text-align: right; 
    }

    .user_id
    {
       background-color:  #4B79A1;
       color: white;
       width: 300px; 
        font-size: 20px;
       text-align: left; 
       border-radius: 8px;
       padding-left: 8px;
    }

    .num
    {
       width: 200px;
       text-align: right; 
       font-family: "Verdana";
       padding-right: 8px;
    }

    tr
    {
        height: 45px;
        font-size: 20px;
    }


    tr:nth-child(odd) 
    { 
        background-color: #4080bf;
    }
    tr:nth-child(even) 
    { 
        background-color:#00aaff;
    }

</style>
"""