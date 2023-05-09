from FRCAPI import callFRCAPI
from TBAAPI import callTBAAPI
import json
import csv

def getMatches(event, team, avg_qls, eins = False):

    qls_matches = callFRCAPI(event, 0, team, 0)
    ply_matches = callFRCAPI(event, 0, team, 1)

    scores_playoffs = []

    auto_scores_qls = []
    auto_scores_playoffs = []

    matches = []
    
    for m in qls_matches['Matches']:
        for t in m['teams']:
            if team == t['teamNumber']:
                if 'Red' in t['station']:
                    matches.append({"matchNumber": m["matchNumber"], "alliance": "Red", "level": "Quals"})
                    auto_scores_qls.append(m["scoreRedAuto"])
                else:
                    matches.append({"matchNumber": m["matchNumber"],"alliance": "Blue", "level": "Quals"})
                    auto_scores_qls.append(m["scoreBlueAuto"])

    for m in ply_matches['Matches']:
        for t in m['teams']:
            if team == t['teamNumber']:
                if 'Red' in t['station']:
                    scores_playoffs.append(m["scoreRedFinal"])
                    matches.append({"matchNumber": m["matchNumber"],"alliance": "Red", "level": "Plays"})
                    auto_scores_playoffs.append(m["scoreRedAuto"])
                else:
                    scores_playoffs.append(m["scoreBlueFinal"])
                    matches.append({"matchNumber": m["matchNumber"], "alliance": "Blue", "level": "Plays"})
                    auto_scores_playoffs.append(m["scoreBlueAuto"])

    avg_score = 0
    avg_auto = 0
    
    if len(scores_playoffs) > 0:            
        if eins:
            avg_score = sum(scores_playoffs)/len(scores_playoffs)
            avg_auto = sum(auto_scores_playoffs)/len(auto_scores_playoffs)
        else:
            avg_score = (avg_qls + sum(scores_playoffs)/len(scores_playoffs))/2
            avg_auto = (sum(auto_scores_qls )+ sum(auto_scores_playoffs))/(len(auto_scores_qls) + len(auto_scores_playoffs))
    
    return avg_score, avg_auto, matches 

def getMatchesDetails(event, team, matches, eins=False):
    
    qls_matches = callFRCAPI(event, 1, team, 0)
    ply_matches = callFRCAPI(event, 1, team, 1)

    gamepieces_qls = []
    gamepieces_playoffs = []


    links_points_qls = []
    links_points_playoffs = []

    chargestations_scores_qls = []
    chargestations_scores_playoffs = []

    i = 0
    
    for m in qls_matches['MatchScores']:
        match_details = matches[i]['alliance']
        scores = m.get('alliances')
        for s in scores:
            if s['alliance'] == match_details:
                gamepieces = s["teleopGamePieceCount"] + s["autoGamePieceCount"]
                gamepieces_qls.append(gamepieces)
                links_points_qls.append(s["linkPoints"])
                chargestations_scores_qls.append(s["totalChargeStationPoints"])
        i+=1
        
    for m in ply_matches['MatchScores']:
        match_details = matches[i]['alliance']
        scores = m.get('alliances')
        for s in scores:
            if s['alliance'] == match_details:
                gamepieces = s["teleopGamePieceCount"] + s["autoGamePieceCount"]
                gamepieces_playoffs.append(gamepieces)
                links_points_playoffs.append(s["linkPoints"])
                chargestations_scores_playoffs.append(s["totalChargeStationPoints"])
                
                
        i+=1
        
    if eins:
        if len(gamepieces_playoffs) > 0:
            avg_game_pieces_score = sum(gamepieces_playoffs)/len(gamepieces_playoffs)
            avg_links_points = sum(links_points_playoffs)/len(links_points_playoffs)
            avg_charge_station = sum(chargestations_scores_playoffs)/len(chargestations_scores_playoffs)
        else:
            avg_game_pieces_score = 0
            avg_links_points = 0
            avg_charge_station = 0
    else:
        avg_game_pieces_score = (sum(gamepieces_qls)+sum(gamepieces_playoffs))/(len(gamepieces_qls)+len(gamepieces_playoffs))
        avg_links_points = (sum(links_points_qls)+sum(links_points_playoffs))/(len(links_points_qls)+len(links_points_playoffs))
        avg_charge_station = (sum(chargestations_scores_qls)+sum(chargestations_scores_playoffs))/(len(chargestations_scores_qls)+len(chargestations_scores_playoffs))
    
    return avg_game_pieces_score, avg_links_points, avg_charge_station
    
    
        

def getRegional(team, event, eins = False):

    team_ranking = callFRCAPI(event, 2, team)
    
    if len(team_ranking['Rankings']) > 0:
        avg_qls_score = team_ranking['Rankings'][0]['qualAverage']
    else:
        eins = True
        avg_qls_score = 0
    
    regional = {}
    
    regional["team"]=team
    regional["event"]=event
    
    matches_data = getMatches(event, team, avg_qls_score, eins)
    match_details = getMatchesDetails(event, team, matches_data[2], eins)  
    
    regional["avg_score"] = matches_data[0]
    regional["avg_score"] = matches_data[1]
    regional["avg_game_pieces_score"] = match_details[0]
    regional["avg_links_points"] = match_details[1]
    regional["avg_charge_station"] = match_details[2]

    return regional

        
        
def getDataSet(filename):
    teams = []

    with open(filename, 'r') as file:
        for line in file:
            team = { "teamNumber" : int(line.rstrip())}
            events = []
            team_events_raw = callTBAAPI(int(line.rstrip()))
            for e in team_events_raw:
                #print(json.dumps(e, indent=4))
                if e["first_event_code"] is not None and e["event_type"] != 2:
                    events.append(e["first_event_code"].upper())
                    #print(e["first_event_code"].upper())
            team["events"] = events
            teams.append(team)
            print("*",end="")
    print("\n")
    print("teams readed")
    print("\n")
    getData(teams)
    

def getData(teams, eins = False):

    data_str_FRC = {}

    len_data = 0

    for t in teams:
        len_data += len(t['events'])
        
    print("Number of events: ",len_data)
    print(len_data)
    for t in teams:
        team = t['teamNumber']
        for e in t['events']:
            event = e
            try:
                reg = getRegional(team, event, eins)
            except:
                print(team)
                continue
            data_str_FRC[str(team)+event] = reg
            len_data-=1
            print(len_data)
            #print(".", end="")

    data = open("data.txt", "w")
    json_obj = json.dumps(data_str_FRC, indent=4)

    data.write(json_obj)
    data.close()

    with open('data.json', 'w') as json_file:
        json.dump(data_str_FRC, json_file, indent=4)


    with open('data.csv', 'w', newline='') as csv_file:
        
        writer = csv.writer(csv_file)
        header = ['team', 'event', 'avg_score', 'avg_game_pieces_score','avg_links_points', 'avg_charge_station']
        writer.writerow(header)
        
        for register in data_str_FRC:
            row = [data_str_FRC[register]['team'], data_str_FRC[register]['event'],data_str_FRC[register]['avg_score'],
                   data_str_FRC[register]['avg_game_pieces_score'],data_str_FRC[register]['avg_links_points'],
                   data_str_FRC[register]['avg_charge_station']]
            writer.writerow(row)
    print("\n")
    print("Finished")
    
    return data_str_FRC, json_obj



