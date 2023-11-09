import gzip
# Library for asyncronously downloading data from S3, likely a better way to do this, will keep in mind for future
#from aiobotocore.session import get_session
import json
import asyncio
import time


# Get starting time, since this code takes a long time to execute its useful to know the total runtime
start = time.time()
# The stats that are collected for each player
stats = ['kills', 'deaths', 'assists', 'turretsDestroyed', 'first_bloods', 'wins', 'losses', 'games_played']
# The name and region of the S3 Bucket containing the data
bucket_name = 'power-rankings-dataset-gprhack'
region = 'us-west-2'

# number of asynchronous workers downloading data,
# kept low because higher numbers did not seem to speed up downloading upon testing
worker_number = 4
# Maximum number of mapping objects from mappings.json to load.
max_mappings = 5000
final_player_stats = []
clean_data = []

# Get s3 bucket object containing game data


def get_team_data(id):
    """ Gets team name and acronym from ID. Will return None if team not found. Used in other files as well"""
    with open('teams.json', 'r') as f:
        teams = json.load(f)
    try:
        # returns (team_name, team_acronym) as tuple length 2
        return [(t['name'], t['acronym']) for t in teams if t['team_id'] == id][0]
    except Exception as e:
        print('Team ID not found: ' + str(e))


# Gets player names and also player team data from ID. If team is not found team value is None
def get_player_data(id):
    """ Gets player data from ID"""
    with open('players.json') as f:
        players = json.load(f)
        # returns (player_handle, first_name, last_name, (team,name, team_acronym)) as a tuple of length 4
    try:
        return [(p['handle'], p['first_name'], p['last_name'], get_team_data(p['home_team_id']), p['home_team_id']) for p in players if p['player_id'] == id][0]
    except IndexError:
        print("Player ID not found")


def map_number(player_number, participants):
    """ Used to get number for mapping in mapping_data.json"""
    if player_number in participants:
        return participants[player_number]


def increment_stat(player_stats, player_id,stat):
    """ Helper function to increment player stats during data collection"""
    if player_stats and player_id is not None:
        player_stats[player_id][stat] += 1


def aggregate_game_data(mapping,events):
    """Takes platform ID and returns dictionary with players alongside given list of stats to get data
     Since there is so much data we do is asyncronously with asyncio module"""
    participants = mapping['participantMapping']
    player_stats = {p:{s:0 for s in stats} for p in participants.values()}

# Iterate though each event in the game file and update stats depending on eventType
    for event in events:
        type = event['eventType']
    # increments turret destruction data
        if type == 'building_destroyed':
           player_number = str(event['lastHitter'])
           if event['buildingType'] == "turret" and not player_number == '0':
               player_id = map_number(player_number, participants)
               increment_stat(player_stats, player_id, 'turretsDestroyed')

        elif type == 'champion_kill':
            # Increments player kills and deaths to player_stats
            player_number = str(event['killer'])
            player_id = map_number(player_number, participants)
            increment_stat(player_stats, player_id, 'kills')
            player_id = map_number(str(event['victim']), participants)
            increment_stat(player_stats, player_id, 'deaths')
            # Adds player assists to player_stats, if no assisters, does nothing
            try:
                for killer in event['deathRecap']:
                    assister = str(killer['casterId'])
                    if assister != player_number:
                        increment_stat(player_stats, player_id, 'assists')
            except KeyError:
                pass
        # Adds first blood to player stats
        elif type == 'champion_kill_special':
            if event['killType'] == 'firstBlood':
                player_number = str(event['killer'])
                player_id = map_number(player_number, participants)
                increment_stat(player_stats, player_id, 'first_bloods')
        # Increments game wins and losses to stats
        elif type == 'game_end':
            winningTeam = event['winningTeam']
            for p in participants:
                player_id = participants[p]
                increment_stat(player_stats, player_id, 'games_played')

                if winningTeam == '100':
                    if 1 < int(p) < 6:
                        increment_stat(player_stats, player_id, 'wins')
                    else:
                        increment_stat(player_stats, player_id, 'losses')

                else:
                    if 5 < int(p) < 11:
                        increment_stat(player_stats, player_id, 'wins')
                    else:
                        increment_stat(player_stats, player_id, 'losses')
    return player_stats

# List of workers asynchronously downloading data
workers = []


# Use asyncronous downloading rather than multithreading or multiprocessing
# Because I/O bound operations such as downloading data are very efficient when done this way
async def worker(name, queue, lock):
    """Worker that will be asynchronously ran to download data faster"""
    jobsDone = 0

    while True:
        # Get a mapping from a queue
        map = await queue.get()
        platformID = map['platformGameId']
        key = 'games/' + platformID + '.json.gz'
        # Asynchronously create a s3 client for data downloading
        session = get_session()
        async with session.create_client('s3', region_name=region) as client:
            try:
                print(f'{name} downloading {key}')
                await asyncio.sleep(0)
                # Download data
                response = await client.get_object(Bucket=bucket_name, Key=key)
                await asyncio.sleep(0)
                jobsDone += 1
                # Ignore headers
                body = await response['Body'].read()

                await asyncio.sleep(0)
                # Decompress Gzipped s3 object
                f = await asyncio.to_thread(gzip.decompress, body)
                await asyncio.sleep(0)
                # Encode it to utf-8
                f = await asyncio.to_thread(f.decode, 'utf-8')
                await asyncio.sleep(0)
                # Load data into a dictionary, get player data from file
                events = await asyncio.to_thread(json.loads, f)
                data = aggregate_game_data(map, events)
                # Use a lock to avoid data corruption
                async with lock:
                    clean_data.append(data)
                    queue.task_done()
            except Exception as e:
                print(str(e) + ' when downloading ' + key)


# Manages asynchronous workers
async def main():
    # Create a queue and a lock
    q = asyncio.Queue()
    lock = asyncio.Lock()
    # Fill queue with mappings
    with open('mapping_data.json', 'r') as f:
        mappings = json.load(f)
        # Ignore max mappings, trying to download all data
        # mappings = mappings[:max_mappings]
        for map in mappings:
            await q.put(map)

    # Create asynchrous workers
    for i in range(worker_number):
        worker_name = f'worker {str(i)}'
        w = asyncio.create_task(worker(worker_name, q, lock))
        print("Created worker " + worker_name)
        workers.append(w)
    # Start asynchronous workers
    await q.join()
    # Stop asynchronous workers when tasks finish
    for work in workers:
        work.cancel()
        print("canceled worker " + str(work))

    await asyncio.gather(*workers, return_exceptions=True)
    print("Data processed in " + str(time.time() - start) + ' seconds')


def combine_clean_data(data):
    """Combines all of the data returned from data downloading and combine it into json file"""
    for game in data:
        for id in game:
            temp = {}
            # (player_handle, first_name, last_name, (team,name, team_acronym))
            player_info = get_player_data(id)
            if player_info is not None and None not in player_info:
                temp['player_name'] = player_info[0]
                temp['team'] = player_info[3]
            temp['id'] = id

            current_stats = game[id]
            temp['performance'] = current_stats
            try:
                current_player = [p for p in final_player_stats if p['id'] == id][0]
                old_stats = current_player['performance']
                new_stats = {}

                for stat in current_stats:
                    for old in old_stats:
                        if stat == old:
                            new_stats[stat] = old_stats[old] + current_stats[stat]

                index = final_player_stats.index(current_player)
                final_player_stats[index]['performance'] = new_stats

            except:
                final_player_stats.append(temp)


# Run functions to accomplish task of getting player data
if __name__ == '__main__':
    #asyncio.run(main())
    with open('fixed_json.json', 'r') as f:
        actual_clean_data = json.load(f)

    combine_clean_data(actual_clean_data)
    with open('final_data.json', 'w') as f:
        json.dump(final_player_stats, f)
