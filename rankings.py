import numpy as np
from teams import *
from dataGrabber import get_player_data
import datetime

# Assumed skill value of missing players
assumedSkill = 30
# Weights used to calculate team skill
ancientWeight = 0.01
oldWeight = 0.01
agedWeight = 0.02
youngWeight = .09
levelWeight = .46
regionWeight = .2
playerWeight = .21
# Caps on the data to eliminate outliers from messing up data MinMaxing
maxGamesPlayed = 5
gamesPlayedCap = 80
averageFbCap = 1.3
averageTdCap = 1.3
KDAcap = 2.7
winrateCap = 2
regionGameSizeCap = 180

# Scaled average firstbloods up to make the number less small
fbScaleValue = 10

# Weights for calculating player skill
wrWeight = .3
kdWeight = .3
fbWeight = .05
tdWeight = .05
gpWeight = .3

# 0-normalizationScale range on normalized values
normalizationScale = 100
# Rosters that have multiple players will be capped to rosterChangeSize with highest skill rating, set to 5
rosterChangeSize = 5

# Remember what ID corresponds to each index of numpy array for players, regions, and teams.
player_data = []
ids = []
idsNoData = []

# Weights related to calculating region skill
rgwrWeight = .6
rggpWeight = .4

region_data = []
team_data = []
regions = []
teams = []

np.set_printoptions(suppress=True)

data = get_final_data()
regionData = get_region_data()
teamData = get_team_stats_json()


# Construct the data into a numpy array
#  {'player_name': 'Kind Jungle', 'team': ['Maryville Saints', 'MU'], 'id': '107577676457789192',
#  'performance': {'kills': 1, 'deaths': 5, 'assists': 0, 'turretsDestroyed': 0, 'first_bloods': 0, 'wins': 0, 'losses': 1, 'games_played': 1}}]

# Kills, Deaths, TurretsDestroyed, first_bloods, wins, losses, games_played
# Construct player data into a numpy array for minMaxing
def player_array():
    for index,player in enumerate(data):
        id = player['id']
        perf = player['performance']
        try:
            gamesPlayed = perf['games_played']
            wins = perf['wins']
            losses = perf['losses']
            kills = perf['kills']
            deaths = perf['deaths']
            firstBloods = perf['first_bloods']
            turretsDestroyed = perf['turretsDestroyed']
        except KeyError as e:
            pass
        try:
            winrate = wins/losses
        except ZeroDivisionError:
            # If no losses the winrate becomes win number
            winrate = wins
        try:
            KDA = kills/deaths
        except ZeroDivisionError:
            # If no deaths KDA just becomes kill count
            KDA = kills

        # Winrate, KDA, Average FirstBlood, Average Turrets destroyed, gamesPlayed, Player skill
        # Multiply by fbScaleValue to make values less small
        # Get average First Bloods and average turrets destroyed
        averageFB = firstBloods/gamesPlayed*fbScaleValue
        averageTD = turretsDestroyed/gamesPlayed

        # Eliminate outliers
        if winrate >= winrateCap:
            winrate = winrateCap
        if KDA >= KDAcap:
            KDA = KDAcap
        if averageFB >= averageFbCap:
            averageFB = averageFbCap
        if averageTD >= averageTdCap:
            averageTD = averageTdCap
        if gamesPlayed >= gamesPlayedCap:
            gamesPlayed = gamesPlayedCap

        # Only store data for players with at least maxGamePlayed games
        if gamesPlayed > maxGamesPlayed:
            # Remember ID that corresponds to array index
            ids.append(id)
            # Round each data point to 2 decimal points
            player_data.append(np.round([winrate, KDA, averageFB, averageTD, gamesPlayed],2))
        else:
            # If less than 5 games add to different list for website purposes
            idsNoData.append(id)
    return np.array(player_data)

# Construct region data into a numpy array
def region_array():
    for region in regionData:
        regions.append(region)
        wins = regionData[region]['wins']
        losses = regionData[region]['losses']
        totalGames = wins + losses
        try:
            winRate = wins/losses
        except ZeroDivisionError:
            winRate = wins

        # If team has regionGameSizeCap then consider it a 100 when normalized
        if totalGames >= regionGameSizeCap:
            totalGames = regionGameSizeCap
        # Also round to 2 decimal points
        region_data.append(np.round([winRate,totalGames],2))
    return np.array(region_data)


# Scales the values to values from 1 to 100 using MinMax scaling
def normalize(array):
    return array / array.max(axis=0) * normalizationScale

# stats = [Winrate, KDA, Average FirstBlood, Average Turrets destroyed, gamesPlayed, Player skill]
# Calculates player skill using weights and collection of stats
def calculate_pSkill(name,array):
    stats = list(array)
    if not stats is None:
        wr = stats[0]
        kd = stats[1]
        fb = stats[2]
        td = stats[3]
        gp = stats[4]
        # Return the stats so I can transparently break down how each value was calculated on the website
        return (wr*wrWeight + kd*kdWeight + fb*fbWeight + td*tdWeight + gp*gpWeight), list(stats)
    return None


# Helper function for calculating region skill
def get_stats(name,array,order):
    for i,o in enumerate(order):
        if o == name.lower() or (o == 'cois' and name == 'COMMONWEALTH OF INDEPENDENT STATES'):
            return array[i]
        if o == 'pcs' and name == 'HONG KONG, MACAU, TAIWAN' or name == 'OCEANIA':
            return array[i]
        if o == 'latin america' and name == 'LATIN AMERICA NORTH':
            return array[i]


# Calculates region skill using full array
def calculate_rSkill(name,array):
    stats = get_stats(name,array,regions)
    wr = stats[0]
    gp = stats[1]
    return wr * rgwrWeight + gp*rggpWeight,stats


# Retrieves region skill based on region name
def get_region_multiplier(region,regionArray):
    index = regions.index(region)
    return calculate_rSkill(region,regionArray)


# Used for sorting tournaments by start date in team array function with key=parameter
def get_dateTime(era):
    date = era['start']
    year, month, day = map(int, date.split('-'))
    return (year, month, day)


# Creates numpy array of team data
def team_array():
    regArray = normalize(region_array())
    p_array = normalize(player_array())
    # Iterate though teams.py team data and add to numpy array for each team
    for team in teamData:
        region = team['region']
        tournaments = team['tournaments']
        roster = team['roster']
        # Get level of team by looking at level of tournaments in tournament history of team
        if tournaments:
            level = tournaments[0]['level']
            # If that tournament has no level information look at the rest of tournaments in history until it finds somethign
            if level is None:
                for t in tournaments:
                    if t['level'] is not None:
                        level = t['level']
                        break
            # get date that every tournament happened and get win and loss data. Sort the list by start date
            history = [{'start':t['startDate'],'wins':t['wins'],'losses':t['losses']} for t in tournaments]
            history.sort(key=get_dateTime)
            # We assume that on average 1 player, or 20% of the roster has been changed,
            # We separate wins and history into three different catagories,
            # winsAncient, winsOld, winsAged, and winsYoung,  representing 4 year old, 3 years old, 2 years old and 1 years old stats respectivly
            # We weigh old data much more lightly than newer data, Depending on how old the newest data is, weight based on player skill more
            winsAncient = 0
            lossesAncient = 0
            winsOld = 0
            lossesOld = 0
            winsAged = 0
            lossesAged = 0
            winsYoung = 0
            lossesYoung = 0
            currentYear = datetime.datetime.now().year
            # Iterate though wins and based on how old the wins or losses are add to different variable
            for era in history:
                year = get_dateTime(era)[0]
                eraWins = era['wins']
                eraLosses = era['losses']
                age = currentYear-year
                if age == 3:
                    winsAncient += eraWins
                    lossesAncient += eraLosses
                if age == 2:
                    winsOld += eraWins
                    lossesOld += eraLosses
                if age == 1:
                    winsAged += eraWins
                    lossesAged += eraLosses
                if age == 0:
                    winsYoung += eraWins
                    lossesYoung += eraLosses
        # Get players in team roster get list of players alongside their respective skills
        players = []
        for pl in roster:
            for i,id in enumerate(ids):
                if pl[0] == id:
                    players.append((pl[0],calculate_pSkill(pl[0],p_array[i])[0]))
                    break
        # Sort the list of players by their team skill, skills of None are put at the bottom
        players.sort(key=lambda r:r[1] if r[1] is not None else float('-inf'))
        # Only get data from rosterChangeSize highest rated players
        players = players[:rosterChangeSize]
        # Calculate average player skill by adding up player skill for each player. if skill is none assume assumedSkill
        totalPlayerSkill = sum([p[1] if p[1] is not None else assumedSkill for p in players])
        averagePlayerSkill = totalPlayerSkill/rosterChangeSize
        # If no losses winrate equals wins
        try:
            youngWinRate = winsYoung/lossesYoung
        except ZeroDivisionError:
            youngWinRate = winsYoung
        try:
            agedWinRate = winsAged / lossesAged
        except ZeroDivisionError:
            agedWinRate = winsAged
        try:
            oldWinRate = winsOld / lossesOld
        except ZeroDivisionError:
            oldWinRate = winsOld
        try:
            ancientWinRate = winsAncient / lossesAncient
        except ZeroDivisionError:
            ancientWinRate = winsAncient
        # If region can be found, get region skill of team for skill calculation
        if region:
            regionSkill = calculate_rSkill(region,regArray)[0]
        else:
            regionSkill = 0
        if level == None:
            level = 1

        result = [regionSkill,level,averagePlayerSkill,youngWinRate,agedWinRate,oldWinRate,ancientWinRate]
        team_data.append(np.round(result,2))
        teams.append((team,winsYoung,winsAged,winsOld,winsAncient,youngWinRate,agedWinRate,oldWinRate,ancientWinRate,averagePlayerSkill,totalPlayerSkill,region,level,regionSkill,lossesYoung,lossesAged,lossesOld,lossesAncient))
    return np.array(team_data)


def calculate_team_skill(name,stats):
# result = [regionSkill,level,averagePlayerSkill,youngWinRate,agedWinRate,oldWinRate,ancientWinRate]
    rs = stats[0]
    lev = stats[1]
    aps = stats[2]
    ywr = stats[3]
    awr = stats[4]
    owr = stats[5]
    anwr = stats[6]
    return (rs * regionWeight + lev*levelWeight + aps*playerWeight + ywr*youngWeight + awr*agedWeight + owr*oldWeight + anwr*ancientWeight),list(stats)

def rank_teams():
    power_rankings = []

    for index,team in enumerate(teams):
        first = team[0]
        second = [i for i in team[1:]]
        # Don't rank any team with no roster information
        if first['roster']:
            tournaments = first['tournaments']
            if tournaments:
                level = tournaments[0]['level']
                if level == None:
                    for t in tournaments:
                        if t['level'] is not None:
                            level = t['level']
            try:
                level = first['level']
            except KeyError:
                level = 1

                #level = 1
            skill = calculate_team_skill(first['id'],t_array[index])
            temp = {'id':first['id'],'name':first['name'],'level':level,'region':first['region'], 'skill':skill[0],'scaledValues':skill[1],'team':first['tournaments'],'region':first['region']}
            #(team, winsYoung, winsAged, winsOld, winsAncient, youngWinRate, agedWinRate, oldWinRate,
            #              ancientWinRate, averagePlayerSkill, totalPlayerSkill, region, level, regionSkill, lossesYoung,
              #            lossesAged, lossesOld, lossesAncient))

            print('second', second)
            #print(second)

            temp['winsYoung'] = second[0]
            temp['winsAged'] = second[1]
            temp['winsOld'] = second[2]
            temp['winsAncient'] = second[3]
            temp['youngWinRate'] = second[4]
            temp['agedWinRate'] = second[5]
            temp['oldWinRate'] = second[6]
            temp['ancientWinRate'] = second[7]
            temp['averagePlayerSkill'] = second[8]
            temp['totalPlayerSkill'] = second[9]
            temp['lossesYoung'] = second[13]
            temp['lossesAged'] = second[14]
            temp['lossesOld'] = second[15]
            temp['lossesAncient'] = second[16]

            power_rankings.append(temp)

    power_rankings.sort(key=lambda p:p['skill'],reverse=True)
    return power_rankings

def migrate_players():
    player_rankings = []
    for i,id in enumerate(ids):
            # stats = [Winrate, KDA, Average FirstBlood, Average Turrets destroyed, gamesPlayed, Player skill]
        wins = get_player_wins(id)
        try:
            skill = calculate_pSkill(id,p_array[i])
        except:
            break
    #return (wr * wrWeight + kd * kdWeight + fb * fbWeight + td * tdWeight + gp * gpWeight), list(stats)
        # Skill, Scaled values, [(p['handle'], p['first_name'], p['last_name'], (t['name'],t['acronym'],p['home_team_id']), 'kills': 16, 'deaths': 113, 'assists': 97, 'turretsDestroyed': 1, 'first_bloods': 1, 'wins': 14, 'losses': 19, 'games_played': 33},player ID
        player_rankings.append([skill[0],skill[1],get_player_data(id),get_player_wins(id),id])
    return player_rankings
 
noIdRankings = []

def migrate_noIds():
    for i,id in enumerate(idsNoData,start=1):
        noIdRankings.append([get_player_data(id),get_player_wins(id),id])
    print('processed {} noData players'.format(i+1))


def migrate_playerRankings(player_rankings):
    for i,id in enumerate(ids):
            # stats = [Winrate, KDA, Average FirstBlood, Average Turrets destroyed, gamesPlayed, Player skill]
        wins = get_player_wins(id)
        try:
            skill = calculate_pSkill(id,p_array[i])
        except:
            break
    player_rankings.append([skill[0],skill[1],get_player_data(id),get_player_wins(id),id])
    print('processed {} players'.format(i+1))


def migrateNoId():
    for i,id in enumerate(idsNoData,start=1):
        noIdRankings = []
        noIdRankings.append([get_player_data(id),get_player_wins(id),id])
        print('processed {} noData players'.format(i+1))
        return noidRankings
    

def rank_regions():
    region_rankings = []
    for region in regions:
        name = region
        wins = regionData[region]['wins']
        losses = regionData[region]['losses']
        gamesPlayed = wins+losses
        skill = calculate_rSkill(region, r_array)
        if region:
            regionSkill = skill[0]
        else:
            regionSkill = 0
        scaledValues = skill[1]
        print(name)
        region_rankings.append({'name':name,'wins':wins,'losses':losses,'gamesPlayed':gamesPlayed,'skill':regionSkill,'scaledValues':list(scaledValues)})
    
    
def dumpData():
    with open('teams_toMigrate.json', 'w') as teams, open('players_toMigrate.json', 'w') as players, open('noDataPlayers_toMigrate.json','w') as ndp, open('region_toMigrate.json','w') as rr:
        json.dump(power_rankings,teams)
        json.dump(region_rankings,rr)

'''            
ancientWeight = .01
oldWeight = .02
agedWeight = .07
youngWeight = .2
levelWeight = .25
regionWeight = .2
playerWeight = .25
'''

if __name__ == '__main__':
    p_array = normalize(player_array())
    t_array = normalize(team_array())
    r_array = normalize(region_array())
    #rank_teams()
    rank_regions()
