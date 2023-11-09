import json

final_team_data = {}
team_wl_data = []
# List that will contain a lot of team data used for skill calculations
teams = []


# Get league data for region purposes
def get_league_data():
    with open('leagues.json', 'r') as f:
        return json.load(f)


# Load data from s3
def get_final_data():
    with open('final_data.json', 'r') as f:
        return json.load(f)


# Load data containing tournament data
def get_tournament_data():
    with open('tournaments.json','r') as f:
        return json.load(f)


# Load data containing league teams
def get_team_json():
    with open('teams.json','r') as f:
        return json.load(f)


# Gets 'region_data.json'
def get_region_data():
    with open('region_data.json', 'r') as f:
        return json.load(f)


# Gets file containing player data from dataGrabber.py
def get_team_stats_json():
    with open('team_stats.json','r') as f:
        return json.load(f)



def get_players_json():
    with open('players.json') as f:
        return json.load(f)

# Team Name: , ID:, Region:, Tournaments: [Name, ID:, StartDate:, EndDate,  Wins:, Losses:, Ties:, Level:
# Roster[ Name, ID,], ChangesSinceLast: }


# Gets player wins and losses for when getting data for website much later
def get_player_wins(id):
    for p in get_final_data():
        if p['id'] == id:
            return p['performance']


tournaments = get_tournament_data()
leagues = get_league_data()


# helper function that gets dictionary containing full tournament data from an ID
def get_tourn_dict(id):
    for tourn in tournaments:
        if tourn['id'] == id:
            return tourn


# Gets the roster of each team and appends that information to the teams list
def get_team_rosters():
    players = get_players_json()
    for player in players:
        home_id = player['home_team_id']
        if home_id:
            for index,team in enumerate(teams):
                if home_id == team['id']:
                    teams[index]['roster'].append((player['player_id'],player['handle']))



# helper function that gets metadata from a tournament ID
def get_tournament_meta(id):
    tdict = get_tourn_dict(id)
    name = tdict['slug']
    region = ''
    level = None
    leagueID = tdict['leagueId']
    # regions = North America EMEA Korea China Brazil CIS Japan Latin America Oceania PCS Turkey Vietnam
    for league in leagues:
        if league['id'] == leagueID:
            region = league['region']

    # This is how competition levels of teams are calculated, by getting information
    # About tournaments team competed in and assigning the team the competition level related to that tournament
    if 'nacl' in name or 'ebl' in name or 'elements' in name:
        level = 1
    elif 'lrs' in name:
        level = 2
    elif 'academy' in name or 'challengers' in name:
        level = 2
    elif (len(name) in (15,16) and 'tcl' not in name and not 'lfl' in name and not 'nlc' in name and 'tal' not in name and not 'opening' in name and not 'gll' in name or 'cblol' in name and not 'ldl' in name and not 'lrs_' in name and not 'nacl' in name) or 'lla' in name or 'lpl' in name:
        level = 3
    elif 'pg' in name or 'liga' in name or 'prime' in name in name or 'tcl' in name or 'lfl' in name or 'nlc' in name or 'volcano' in name or 'flow' in name or 'honor' in name or 'stars' in name or 'lco' in name or 'ddh' in name:
        level = 2
    elif 'arabian' in name or 'gll' in name or 'elite' in name or 'greek' in name or 'college' in name or 'proving' in name or 'golden' in name or 'balkan' in name or 'hitpoint' in name or 'challengers' in name or 'nacl' in name or 'tal' in name or 'amateur' in name:
        level = 1

    return [tdict['name'], tdict['slug'], tdict['leagueId'], tdict['startDate'], tdict['endDate'], region, level]


# Gets team roster by scanning tournament for game with team present and retrieving roster
# Extra playes that did not participate in game retrieved, ignores players with least data for final calculations
# This one directly returns the rosters unlike the previous and is used by rankings.py to get roster data from tournaments,
# I dont end up using this because I deemed it easier later on to just get rosters by the other method
# This method in uneccesary
def get_roster(tourn,teamID):
    stages = tourn['stages']
    for stage in stages:
        sections = stage['sections']
        for section in sections:
            matches = section['matches']
            for match in matches:
                teams = match['teams']
                for team in teams:
                    if team['id'] == teamID:
                        return team['players']


# [participant1: [ID, Result, {Record}] Participants2: [ID, Result, {Record}]
# Parses the tournaments.json file to get every game in a tournament
# only display team id and game outcome for each game in tournament
def get_games(tournament):
    stages = tournament['stages']
    competitors = set()
    matchData = []
    for stage in stages:
        sections = stage['sections']
        for section in sections:
            matches = section['matches']
            for match in matches:
                games = match['games']
                for game in games:
                    teams = game['teams']
                    gameData = []
                    if game['state'] == 'completed':
                        for team in teams:
                            id = team['id']
                            participants = {}
                            participants['id'] = id
                            competitors.add(id)
                            participants['result'] =  team['result']['outcome']
                            gameData.append(participants)
                        matchData.append(gameData)
    return matchData,competitors


# Aggregates every win/loss into one list for each team.
# Then, collects all the data and returns a bunch of stats for each team used
# In skill calculations
def get_teams(tournament):
    tournID = tournament['id']
    data = get_games(tournament)
    meta = get_tournament_meta(tournID)
    # [Name, Slug, leagueID,Start,End,stagesList]
    matches = data[0]
    ids = data[1]
    result = []
    for id in ids:
        wins = 0
        losses = 0
        for match in matches:
            for game in match:
                if game['id'] == id:
                    res = game['result']
                    if res == 'win':
                        wins += 1
                    elif res == 'loss' or res == 'forfeit':
                        losses += 1

        stats = {'wins':wins,'losses':losses}
        teamStats = {'id':id,'stats':stats}
        result.append(teamStats)
# Append every team to the corresponding tournaments list within the team in the teams list
    for r in result:
        # meta = [Name, Slug, leagueID,Start,End,stagesList,Region]
        if meta is not None:
            date = meta[3]
            temp = {'id':tournID,'leagueID':meta[2],'name':meta[1],'startDate':date,'endDate':meta[4]}#,'roster':get_roster(tournament,r['id'])}
            temp['wins'] = r['stats']['wins']
            temp['losses'] = r['stats']['losses']
            # Assigns region and level to team based on tournament level and region
            # gotten from the get_tournament_meta() function
            temp['region'] = meta[5]
            temp['level'] = meta[6]

            for index,team in enumerate(teams):
                if team['id'] == r['id']:
                    teams[index]['tournaments'].append(temp)
                    # Do not assign teams regions to 'international'
                    if not meta[5] == 'INTERNATIONAL':
                        teams[index]['region'] = meta[5]

    return result

# Retrieves data about specific region winrates
def get_region():
    emeaWins = 0
    emeaLosses = 0
    japanWins = 0
    japanLosses = 0
    hkmtWins = 0
    hkmtLosses = 0
    chinaWins = 0
    chinaLosses = 0
    naWins = 0
    naLosses = 0
    latamWins = 0
    latamLosses = 0
    koreaWins = 0
    koreaLosses = 0
    vietWins = 0
    vietLosses = 0
    brazilWins = 0
    brazilLosses = 0
    coisWins = 0
    coisLosses = 0
    oceanWins = 0
    oceanLosses = 0

# Ignore all star and TFT rising legends,which are also considered international
    # Gets region data based on teams winrates and their regions
    for league in leagues:
        if 'worlds' in league['slug'] or 'msi' in league['slug']:
            for tourn in league['tournaments']:
                tourn = get_tourn_dict(tourn['id'])
                try:
                    results = get_teams(tourn)
                except TypeError:
                    continue

                for result in results:
                    for team in teams:
                        if team['id'] == result['id']:
                            try:
                                region = team['region'].lower()
                            except AttributeError:
                                region = None
                            stats = result['stats']
                            wins = stats['wins']
                            losses = stats['losses']
                            # Add stats based on region
                            if region == 'china':
                                chinaWins += wins
                                chinaLosses += losses
                            if region == 'korea':
                                koreaWins += wins
                                koreaLosses += losses
                            if region == 'north america':
                                naWins += wins
                                naLosses += losses
                            if region == 'japan':
                                japanWins += wins
                                japanLosses += losses
                            if region == 'emea':
                                emeaWins += wins
                                emeaLosses += losses
                            if region == 'brazil':
                                brazilWins += wins
                                brazilLosses += losses
                            if region == 'latin america':
                                latamWins += wins
                                latamLosses += losses
                            if region == 'hong kong, macau, taiwan':
                                hkmtWins += wins
                                hkmtLosses += losses
                            if region == 'commonwealth of independent states':
                                coisWins += wins
                                coisLosses += losses
                            if region == 'oceania':
                                oceanWins += wins
                                oceanLosses += losses
                            if region == 'vietnam':
                                vietWins += wins
                                vietLosses += losses
    # Add all of this data to a dictionary and return it
    regionStats = {'brazil': {'wins': brazilWins, 'losses': brazilLosses}}
    regionStats['north america'] = {'wins':naWins,'losses':naLosses}
    regionStats['vietnam'] = {'wins': vietWins, 'losses': vietLosses}
    regionStats['korea'] = {'wins': koreaWins, 'losses': koreaLosses}
    regionStats['china'] = {'wins': chinaWins, 'losses': chinaLosses}
    regionStats['emea'] = {'wins': emeaWins, 'losses': emeaLosses}
    regionStats['japan'] = {'wins': japanWins, 'losses': japanLosses}
    regionStats['latin america'] = {'wins': latamWins, 'losses': latamLosses}
    regionStats['pcs'] = {'wins': hkmtWins, 'losses': hkmtLosses}
    regionStats['cois'] = {'wins': coisWins, 'losses': coisLosses}
    return regionStats


# put a list of every team into teams.json so functions that add team data by searching the list for a team
# and adding the data to the corresponding team wont break
def construct_teams(data):
    for team in data:
        teamData = {'id': team['team_id'], 'name': team['name'], 'region': None, 'tournaments': [], 'roster': [], }
        teams.append(teamData)


# Use functions to accomplish task
if __name__ == '__main__':
    team_json = get_team_json()
    construct_teams(team_json)
    get_team_rosters()

    for tourn in tournaments:
        get_teams(tourn)

    #with open('team_stats.json','w') as f:
        #json.dump(teams,f)

    #with open('region_data.json','w') as f:
    #    regDat = get_region()
    #    json.dump(regDat,f)


    #for team in teams:
       # print(team)
        #if team['tournaments']:
            #print(team['name'],team['tournaments'][0]['level'],team['tournaments'][0])
