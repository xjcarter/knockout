

def generate_player_report(report_week,
                          players,
                          user_id,
                          scoreboard,
                          vitals,
                          summary_info,
                          team_freqs,
                          nfl_teams):

    header_table = """
    <br>
    <span style="font-family: Lucida Sans; font-size:18px; color:#000000;"><strong>{week}&nbsp;&nbsp;Current Standings</strong></span> 
    <br>
    <br>
    <table width="500" border="1" cellpadding="6" cellspacing="0">
      <tr>
        <td width="400" height="40" style="font-family: Lucida Sans; font-size: 16px; color: #000000;">
            <strong>{user_id}:</strong>&nbsp;&nbsp;&nbsp;{box_score}
        </td>
        <td width="100" height="40" align="center" style="font-family:  Lucida Sans; font-size: 16px; color: #ffffff; background-color:{alert}">
            <strong>{status}</strong>
        </td>
      </tr>
    </table>

    <br>
    <span style="font-family: Lucida Console; font-size:12px; color:#000000;">
    <strong>PLAYER STATUS:</strong><br>
    PERFECT: All selections to date have been winners.<br>
    ALIVE:&nbsp;&nbsp;&nbsp;Player still active, but Mulligan was used.<br>
    DEAD:&nbsp;&nbsp;&nbsp;&nbsp;Player has been elimnated.
    </span>
    <br>

    <br>
    <table width="400" border="1" cellpadding="6" cellspacing="0">
      <tr>
        <td width="300" height="40" style="font-family: Lucida Sans; font-size: 16px; color: #000000;background-color: #d1d1e0">
            <strong>Participants</strong> 
        </td>
        <td width="100" height="40" align="center" style="font-family:  Lucida Sans; font-size: 16px; color: #000000; background-color:#d1d1e0">
            <strong>Count</strong>
        </td>
      </tr>
    """
    header_row = """
      <tr>
        <td width="300" height="20" style="font-family:  Lucida Sans; font-size: 14px; color: #000000;">
            {category}
        </td>
        <td width="100" height="20" align="center" style="font-family:  Lucida Sans; font-size: 14px; color: #000000;">
            {amount} 
        </td>
      </tr>
    """

    team_table = """
    <br>
    <span style="font-family: Lucida Sans; font-size:18px; color:#000000;"><strong>Player Selections through {week}</strong></span> 
    <br>
    <br>
    <table width="400" border="1" cellpadding="6" cellspacing="0">
      <tr>
        <td width="300" height="40" style="font-family: Lucida Sans; font-size: 16px; color: #000000;background-color: #d1d1e0">
            <strong>Team</strong> 
        </td>
        <td width="100" height="40" align="center" style="font-family:  Lucida Sans; font-size: 16px; color: #000000; background-color:#d1d1e0">
            <strong># Players Used</strong>
        </td>
            <td width="100" height="40" align="center" style="font-family:  Lucida Sans; font-size: 16px; color: #000000; background-color:#d1d1e0">
            <strong>% of Pool</strong>
        </td>
      </tr>
    """

    team_row = """
      <tr>
        <td width="300" height="20" style="font-family:  Lucida Sans; font-size: 14px; color: #000000;">
            {team}
        </td>
        <td width="100" height="20" align="center" style="font-family:  Lucida Sans; font-size: 14px; color: #000000;">
            {count} 
        </td>
        <td width="100" height="20" align="center" style="font-family:  Lucida Sans; font-size: 14px; color: #000000;">
            {pp} % 
        </td>
      </tr>
    """

    last_pick = vitals['used_path'][report_week-1] 
    box_score = scoreboard[report_week-1][last_pick]
    outcome = 'LOSS - '
    if last_pick in scoreboard[report_week-1]['winners']:
        outcome = 'WIN - '
    box_score = outcome + box_score

    alert = { 'PERFECT':'#00b300', 
              'ALIVE': '#006600',
              'DEAD': '#000000',
              'WINNER': '#0080ff'
            }

    status = vitals['status']
    if vitals['falls'] ==0: status = 'PERFECT'

    wkstr = 'WEEK %02d' % report_week
    header_table = header_table.format(week=wkstr,user_id=user_id,box_score=box_score,status=status,alert=alert[status])
    for k,v in summary_info:
        new_row = header_row.format(category=k,amount=v)
        header_table += new_row 

    header_table += "</table>"

    team_table = team_table.format(week=wkstr)
    for k in team_freqs:
        v = team_freqs[k]
        pp = int(100 * float(v)/players)
        team_table += team_row.format(team=nfl_teams[k],count=v,pp=pp)

    team_table += "</table>"

    return header_table + "<br>" + team_table



def generate_commissioner_report(report_week, summary_info):

    table_row = """
      <tr>
        <td width="300" height="20" style="font-family:  Verdana; font-size: 14px; color: #000000;">
            {category}
        </td>
        <td width="100" height="20" align="center" style="font-family:  Verdana; font-size: 14px; color: #000000;">
            {amount} 
        </td>
      </tr>
    """

    report_table = """
    <div style="position: absolute; top: 10px; left: 50px">
    <br>
    <span style="font-family: Verdana; font-size:18px; color:#000000;"><strong>{week}&nbsp;&nbsp;Current Standings</strong></span> 
    <br>
    <br>
    <table width="400" border="1" cellpadding="6" cellspacing="0">
      <tr>
        <td width="300" height="40" style="font-family: Verdana; font-size: 16px; color: #000000;background-color: #d1d1e0">
            <strong>Participants</strong> 
        </td>
        <td width="100" height="40" align="center" style="font-family:  Verdana; font-size: 16px; color: #000000; background-color:#d1d1e0">
            <strong>Count</strong>
        </td>
      </tr>
    """

    wkstr = 'WEEK %02d' % report_week
    report_table = report_table.format(week=wkstr)
    for k,v in summary_info:
        new_row = table_row.format(category=k,amount=v)
        report_table += new_row

    report_table += "</table></div>"

    return  report_table


