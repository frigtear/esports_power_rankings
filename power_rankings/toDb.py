import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE","power_rankings.settings")
django.setup()

from rankings import models

with open('players_toMigrate.json','r') as players, open('teams_toMigrate.json','r') as teams, open('noDataPlayers_toMigrate.json','r') as ndp,open('region_toMigrate.json','r') as rtm:
    teamData = json.load(teams)
    playerData = json.load(players)
    ndpData = json.load(ndp)
    regionData = json.load(rtm)


def save_regions():
    for region in regionData[:10]:
        name, wins, losses, gamesPlayed, skill, scaledValues, = region['name'], region['wins'], region['losses'], \
        region['gamesPlayed'], region['skill'], region['scaledValues']
        scaledWR, scaledGP = scaledValues[0], scaledValues[1]
        r = models.Region(name=name, wins=wins, losses=losses, gamesPlayed=gamesPlayed, skill=skill, scaledWR=scaledWR,
                   scaledGamesPlayed=scaledGP)
        print(r.name)
        r.save()


def save_teams():
    for rank,team in enumerate(teamData,start=1):
        scaled = team['scaledValues']
        print(rank)
        team_id,team_name,skill,rank,level,avgPlayerSkill,totalPlayerSkill= team['id'],team['name'],team['skill'],rank,team['level'],team['averagePlayerSkill'],team['totalPlayerSkill']
        youngWins, youngLosses, agedWins, agedLosses, oldWins, oldLosses, ancientWins, ancientLosses = team['winsYoung'],team['lossesYoung'],team['winsAged'],team['lossesAged'],team['winsOld'],team['lossesOld'],team['winsAncient'],team['lossesAncient']
        # result = [regionSkill,level,averagePlayerSkill,youngWinRate,agedWinRate,oldWinRate,ancientWinRate]
        scaledAncientWR,scaledOldWR,scaledAgedWR,scaledYoungWR,scaledPlayerSkill,scaledLevel = scaled[6],scaled[5],scaled[4],scaled[3],scaled[2],scaled[1]
        t = models.Team(team_id=team_id,name=team_name,skill=skill,rank=rank,level=level,region=None,scaledLevel=scaledLevel,avgPlayerSkill=avgPlayerSkill,scaledPlayerSkill=scaledPlayerSkill,totalPlayerSkill=totalPlayerSkill,youngWins=youngWins,youngLosses=youngLosses,scaledYoungWR = scaledYoungWR,agedWins=agedWins,agedLosses=agedLosses,scaledAgedWR=scaledAgedWR,oldWins=oldWins,oldLosses=oldLosses,scaledOldWR=scaledOldWR,ancientWins=ancientWins,ancientLosses=ancientLosses,scaledAncientWR=scaledAncientWR)

        if team['region'] is None:
            team['region'] = ''

        regionName = team['region'].lower()

        if regionName == 'hong kong, macau, taiwan' or regionName == 'oceania':
            regionName = 'pcs'
        try:
            if regionName:
                region = models.Region.objects.get(name=regionName)
        except models.Region.DoesNotExist:
            print('not found',region)

        if not region:
            region = None

        t.region = region
        t.save()


def save_players():
    for player in playerData:
        try:
            skill,scaledValues,info,perf,player_id = player[0],player[1],player[2],player[3],int(player[4])
        except IndexError:
            print(player)
            continue
        # ["Orca", "GUO", "CHENG-HAN", ["Deep Cross Gaming", "DCG"],id],
        #{"kills": 16, "deaths": 113, "assists": 97, "turretsDestroyed": 1, "first_bloods": 1, "wins": 14, "losses": 19,"games_played": 33}
        # Skill, Scaled values, [(p['handle'], p['first_name'], p['last_name'], (t['name'],t['acronym'],p['home_team_id']), 'kills': 16, 'deaths': 113, 'assists': 97, 'turretsDestroyed': 1, 'first_bloods': 1, 'wins': 14, 'losses': 19, 'games_played': 33},player ID

        kills,deaths,assists,td,fb,wins,losses,games_played = perf['kills'],perf['deaths'],perf['assists'],perf['turretsDestroyed'],perf['first_bloods'],perf['wins'],perf['losses'],perf['games_played']
        if info:
            handle,first_name,last_name,team_id = info[0],info[1],info[2],info[4]
        else:
            first_name, last_name, handle, team = None,None,None,None
        # [57.49999999999999, 14.444444444444443, 27.69230769230769, 16.153846153846153, 70.0]
        scaledwr,scaledkd,scaledfb,scaledtd,scaledgp = scaledValues[0],scaledValues[1], scaledValues[2],scaledValues[3],scaledValues[4]
        p = models.Player(player_id=player_id,first_name=first_name,last_name=last_name,team=None,handle=handle,skill=skill, kills=kills,deaths = deaths,avgTD=td,avgFB=fb,wins=wins,losses=losses,games_played=games_played,scaledWR=scaledwr,scaledKD=scaledkd,scaledFB=scaledfb,scaledTD=scaledtd,scaledGP=scaledgp)
        try:
            #print(int(team))
            team = models.Team.objects.get(team_id=team_id)
        except models.Team.DoesNotExist:
            team = None
        finally:
            p.team = team
        try:
            p.save()
        except ValueError:
            print('ValueError with {}'.format(player))
            continue

def save_noDataPlayers():
    #[(p['handle'], p['first_name'], p['last_name'], (t['name'], t['acronym'], p['home_team_id']), 'kills': 16, 'deaths': 113, 'assists': 97, 'turretsDestroyed': 1, 'first_bloods': 1, 'wins': 14, 'losses': 19, 'games_played': 33},id
    for player in ndpData:
        try:
             info, perf, player_id = player[0], player[1], player[2]
        except IndexError:
            print(player)
            continue
        print(perf)
        try:
            kills,deaths,assists,td,fb,wins,losses,games_played = perf['kills'],perf['deaths'],perf['assists'],perf['turretsDestroyed'],perf['first_bloods'],perf['wins'],perf['losses'],perf['games_played']
        except KeyError:
            kills, deaths, assists, td, fb, wins, losses, games_played = 0,0,0,0,0,0,0,0
        if info:
            handle,first_name,last_name,team_id = info[0],info[1],info[2],info[4]
        else:
            first_name, last_name, handle, team = None,None,None,None
        print(player_id)
        p = models.Player(player_id=player_id,first_name=first_name,last_name=last_name,team=None,handle=handle,skill=None, kills=kills,deaths = deaths,avgTD=td,avgFB=fb,wins=wins,losses=losses,games_played=games_played,scaledWR=-1,scaledKD=-1,scaledFB=-1,scaledTD=-1,scaledGP=-1)
        try:
            team = models.Team.objects.get(team_id=team_id)
        except models.Team.DoesNotExist:
            team = None
        finally:
            p.team = team
            try:
                p.save()
            except ValueError:
                pass


if __name__ == '__main__':
    save_regions()
    save_teams()
    save_players()
    save_noDataPlayers()
    #save_regions()

#print(teamData)