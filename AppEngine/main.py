import datetime, flask, json, math, time, logging
import googlemaps, pytz, requests
from decimal import Decimal
from enum import Enum
from constants import *
from userVars import *
from privateUserVars import *

GMAPS = googlemaps.Client(key = GMAP_API_KEY)

LATEST_FILTER_ETAG = None
SEEN_LIST = []
SEEN_RAID_LIST = []

app = Flask(__name__)

class Scan(Enum):
	DEBUG = -1
	RAID = 0
	RARE_MON = 1
	HIGH_MON = 2
	PERFECT_MON = 3
	EVENT_MON = 4

def getAddress(lat, lng):
	locWhitelist = [
		'establishment',
		'premise',
		'route',
		'street_number'
	]
	returnArr = []
	try:
		res = GMAPS.reverse_geocode((lat, lng))
		for component in res[0]['address_components']:
			for cType in component['types']:
				if cType in locWhitelist:
					returnArr.append(component['short_name'])
					break
		if len(returnArr) == 0:
			return None
		else:
			return ' '.join(returnArr)
	except:
		return None

def getDiscordString(type, obj):
	discordStrArray = []
	if type == Scan.RAID:
		if obj['pokemon_id'] == '0':
			discordStrArray = [
				'EX' if ('is_exclusive' in obj and obj['is_exclusive'] == '1') else ('T' + obj['level']),
				getGymName(obj),
				getTimeString(obj['raid_start']) + '.'
			]
		else:
			discordStrArray = [
				getPokemonNameFromObj(obj),
				'raid at',
				getGymName(obj),
				'until',
				getTimeString(obj['raid_end']) + '.'
			]
			if obj['move1'] != '0' and obj['move2'] != '0':
				discordStrArray.append(getMoveName(int(obj['move1'])) + ', ' + getMoveName(int(obj['move2'])) + '.')
	elif type == Scan.DEBUG:
		discordStrArray = [
			'Invalid pokemon ID from',
			obj['type'],
			'('
			'Raid' if obj['type'] == Scan.RAID else 'Event' if obj['type'] == Scan.EVENT_MON else 'Pokemon'
			'): ',
			obj['name']
		]
	else:
		discordStrArray.append(getPokemonNameFromObj(obj))
		if validIV(obj):
			discordStrArray.append('{}%'.format(getIVPercentage(obj)))
		if obj['cp'] != '-1':
			stri = '({}CP'.format(obj['cp'])
			if validIV(obj):
				stri += ' L{} {}{}{}'.format(
					obj['level'],
					format(int(obj['attack']), 'X'),
					format(int(obj['defence']), 'X'),
					format(int(obj['stamina']), 'X')
				)
			discordStrArray.append(stri + ')')
		discordStrArray += [
			'until',
			getTimeString(obj['despawn']),
			'(' + getTimeDifferenceString(obj['despawn']) + ').'
		]
		addr = getAddress(obj['lat'], obj['lng'])
		if addr is not None:
			discordStrArray.append(addr + '.')
		# un-indent the line below one time to get map directions for raids
		discordStrArray.append(getGoogleMapsURL(obj['lat'], obj['lng']))
	return ' '.join(discordStrArray)

def getGoogleMapsURL(lat, lng):
	return 'http://maps.google.com/maps?q={},{}'.format(lat, lng)

def getGymName(obj):
	key = '{}{}'.format(obj['lat'], obj['lng'])
	if key in GYM_NAMES:
		return GYM_NAMES[key]
	else:
		return '{},{}'.format(obj['lat'], obj['lng'])

def getHeaders(url):
	return {
		'Accept': '/',
    'Accept-Encoding': 'gzip, deflate', #, br
		'Accept-Language': 'en-US,en;q=0.5',
		'Host': 'sydneypogomap.com',
		'Referer': url
	}

def getIVPercentage(pok):
	return int(round((int(pok['attack']) + int(pok['defence']) + int(pok['stamina'])) / 0.45))

def getMoveName(mID):
	if mID in MOVE_NAMES:
		return MOVE_NAMES[mID]
	else:
		return 'MoveID: {}'.format(mID)

def getPokemonID(pName):
	try:
		return POKEMON_NAMES.index(pName) + 1
	except ValueError:
		return None

def getPokemonName(pID):
	if len(POKEMON_NAMES) >= pID:
		return POKEMON_NAMES[pID - 1]
	else:
		return 'PokemonID: {}'.format(pID)
		
def getPokemonNameFromObj(pok):
	# TODO: ditto disguise
	formName = ''
	if 'form' in pok and pok['form'] != '0' and pok['form'] != '-1':
		if pok['pokemon_id'] == '201': # unown
			formName = ' - {}'.format(chr(int(pok['form']) + 64))
		elif pok['form'] == '80':
			formName = ' Alolan'
	return getPokemonName(int(pok['pokemon_id'])) + formName

def getTimeString(utcTime):
	tz = pytz.timezone(LOCATION_STRING)
	return datetime.datetime.fromtimestamp(int(utcTime), tz).strftime('%H:%M:%S')

def getTimeDifferenceString(utcTime):
	mins, secs = divmod((datetime.datetime.fromtimestamp(int(utcTime)) - datetime.datetime.now()).total_seconds(), 60)
	return '{}m{:0>2}s'.format(int(mins), int(math.floor(secs)))

def getURL():
	return 'https://sydneypogomap.com/query2.php?since=0&mons={}&bounds={}'.format(','.join(str(x) for x in range(1, MAX_MON_ID)), ','.join(str(x) for x in POKEMON_AREA))

def isDespawned(spawn):
	endTime = None
	if 'despawn' in spawn:
		endTime = int(spawn['despawn'])
	elif spawn['pokemon_id'] == '0': # unhatched egg
		endTime = int(spawn['raid_start'])
	else:
		endTime = int(spawn['raid_end'])
	return datetime.datetime.now() > datetime.datetime.fromtimestamp(endTime)

def isEvent(pok):
	return int(pok['pokemon_id']) in EVENT_SPAWNS

def isHighIV(pok):
	pid = int(pok['pokemon_id'])
	if validIV(pok):
		if pid in POKEMON and POKEMON[pid] is not None:
			return getIVPercentage(pok) >= POKEMON[pid]
		else:
			return getIVPercentage(pok) >= 90
	return False

def isPerfectIV(pok):
	return validIV(pok) and getIVPercentage(pok) == 100

def isRaidValuable(raid):
	rlevel = int(raid['level'])
	return rlevel in RAIDS and (RAIDS[rlevel] is None or int(raid['pokemon_id']) in RAIDS[rlevel])

def isRaidWithinBoundaries(raid):
	# TODO: currently only works with rectangles that dont go over the lat/lng boundaries where the sign flips
	# shapely's polygon and ".contains" should work
	rlat = Decimal(raid['lat'])
	rlng = Decimal(raid['lng'])
	return rlat >= RAID_AREA['S'] and rlat <= RAID_AREA['N'] and rlng >= RAID_AREA['W'] and rlng <= RAID_AREA['E']

def isRare(pok):
	return int(pok['pokemon_id']) in POKEMON

def parseEventSpawns(mons):
	global EVENT_SPAWNS
	for pok in mons:
		pID = getPokemonID(pok)
		if pID is not None:
			EVENT_SPAWNS[pok] = mons[pok]
		else:
			postLoadError(Scan.EVENT_MON, pok)

def parseGymNames(gymNames):
	global GYM_NAMES
	GYM_NAMES = gymNames

def parseMaxMonID(monID):
	global MAX_MON_ID
	MAX_MON_ID = monID
	# check if you have input something higher than your max id
	for pID in POKEMON.keys():
		try:
			pIDX = int(pID)
		except:
			continue
		if MAX_MON_ID is None or pIDX > MAX_MON_ID:
			MAX_MON_ID = pIDX

def parsePokemon(mons):
	global POKEMON
	for pok in mons:
		pID = getPokemonID(pok)
		if pID is not None:
			POKEMON[pok] = mons[pok]
		else:
			postLoadError(Scan.RARE_MON, pok)

def parsePokemonArea(area):
	global POKEMON_AREA
	# this is the order that *pogomap expects
	POKEMON_AREA = [ area['W'], area['E'], area['S'], area['N'] ]

def parseRaidArea(area):
	global RAID_AREA
	RAID_AREA = area

def parseRaidTime(timeStr):
	global EARLIEST_RAID_TIME
	EARLIEST_RAID_TIME = timeStr

def parseRaids(raidsLocal):
	global RAIDS
	for tier in raidsLocal:
		if isinstance(raidsLocal[tier], list):
			RAIDS[tier] = []
			for pokemonName in raidsLocal[tier]:
				pID = getPokemonID(pokemonName)
				if pID is not None:
					RAIDS[tier].append(pID)
				else:
					postLoadError(Scan.RAID, pokemonName)
		else:
			RAIDS[tier] = raidsLocal[tier]

def parseResponse(res):
	# TODO: can't get brotli working on GAE
	# ImportError: dynamic module does not define init function (init_brotli)
	''' if res.headers['Content-Encoding'] == 'br':
		return json.loads(brotli.decompress(res.content))
	else: '''
	return res.json()

def postDiscord(type, obj, debug=False):
	response = requests.post(
		headers = { 'Content-Type':  'application/json' },
		url = WEBHOOKS[type] if not debug else DEBUG_DISCORD,
		data = '{"content":"' + getDiscordString(type, obj) + '"}'
	)

def postLoadError(type, name):
	obj = {
		'type': type,
		'name': name
	}
	postDiscord(Scan.DEBUG, obj, True)

def raidIsSeen(raid):
	# use the commented one if you want another post on hatch time
	# return raid in SEEN_RAID_LIST
	for r in SEEN_RAID_LIST:
		if r['gym_name'] == raid['gym_name']:
			return True
	return False

def raidTooEarly(raid):
	# TODO: this doesn't seem to work
	if EARLIEST_RAID_TIME is None:
		return False
	else:
		tz = pytz.timezone(LOCATION_STRING)
		spawnTime = datetime.datetime.fromtimestamp(int(raid['raid_start']), tz)
		split = EARLIEST_RAID_TIME.split(':')
		earliestTime = datetime.datetime(spawnTime.year, spawnTime.month, spawnTime.day, int(split[0]), int(split[1]), 0, 0, tz)
		return spawnTime < earliestTime

def validIV(pok):
	return pok['attack'] != '-1' and pok['defence'] != '-1' and pok['stamina'] != '-1'

@app.route('/clear')
def clear():
	global SEEN_LIST
	global SEEN_RAID_LIST
	upperBound = int(time.time()) - 600 # 10 min buffer
	for pok in SEEN_LIST:
		endTime = int(pok['despawn'])
		if endTime < upperBound:
			SEEN_LIST.remove(pok)
	for raid in SEEN_RAID_LIST:
		endTime = int(raid['raid_end'])
		if endTime < upperBound:
			logging.info('removing raid')
			logging.info(raid)
			SEEN_RAID_LIST.remove(raid)

@app.route('/pokemon')
def pokemon():
	global SEEN_LIST
	response = requests.get(
		url = getURL(),
		headers = getHeaders('https://sydneypogomap.com/')
	)
	monList = parseResponse(response)
	if 'pokemons' not in monList:
		return
	for pok in monList['pokemons']:
		if not pok in SEEN_LIST and not isDespawned(pok):
			SEEN_LIST.append(pok)
			if isPerfectIV(pok):
				postDiscord(Scan.PERFECT_MON, pok)
			elif isHighIV(pok):
				postDiscord(Scan.HIGH_MON, pok)
			elif isRare(pok):
				postDiscord(Scan.RARE_MON, pok)
			elif isEvent(pok):
				postDiscord(Scan.EVENT_MON, pok)

@app.route('/raids')
def raids():
	global SEEN_RAID_LIST
	response = requests.get(
		url = 'https://sydneypogomap.com/raids.php',
		headers = getHeaders('https://sydneypogomap.com/gym.html')
	)
	raidList = parseResponse(response)
	if 'raids' not in raidList:
		return
	for raid in raidList['raids']:
		if not raidIsSeen(raid) and not isDespawned(raid) and not raidTooEarly(raid):
			SEEN_RAID_LIST.append(raid)
			if isRaidValuable(raid) and isRaidWithinBoundaries(raid):
				postDiscord(Scan.RAID, raid, True)

@app.route('/update')
def update():
	global LATEST_FILTER_ETAG
	global MAX_MON_ID
	response = requests.get( url = FILTER_URL )
	if 'ETag' not in response.headers or LATEST_FILTER_ETAG == response.headers['ETag']:
		# if not changed since last time then dont bother updating
		return
	resObj = response.json()
	parseRaidTime(resObj['earliest_raid_time'])
	parseRaidArea(resObj['raid_area'])
	parseGymNames(resObj['gym_names'])
	parseRaids(resObj['raids'])
	parsePokemonArea(resObj['pokemon_area'])
	parsePokemon(resObj['pokemon'])
	parseEventSpawns(resObj['event_spawns'])
	parseMaxMonID(resObj['max_mon_id'])
	LATEST_FILTER_ETAG = response.headers['ETag']