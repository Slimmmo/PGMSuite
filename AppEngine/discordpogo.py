import datetime, json, math, time, webapp2
import googlemaps, pytz, requests
from decimal import Decimal
from enum import Enum
from constants import *
from userVars import *
from privateUserVars import *

GMAPS = googlemaps.Client(key = GMAP_API_KEY)

LATEST_ETAG = None
# MAX_MON_ID = None
# POKEMON = {}
# RAIDS = {}
SEEN_LIST = []
SEEN_RAID_LIST = []

class Scan(Enum):
	RAID = 0
	RARE_MON = 1
	HIGH_MON = 2
	PERFECT_MON = 3

def findMaxMonID():
	global MAX_MON_ID
	for pID in POKEMON.keys():
		try:
			pIDX = int(pID)
		except:
			continue
		if MAX_MON_ID is None or pIDX > MAX_MON_ID:
			MAX_MON_ID = pIDX

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
				'Level',
				obj['level'],
				'raid at',
				getGymName(obj),
				'starting at',
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
	else:
		discordStrArray.append(getPokemonNameFromObj(obj))
		if validIV(obj):
			discordStrArray.append('{}%'.format(getIVPercentage(obj)))
		if obj['cp'] != '-1':
			stri = '({}CP'.format(obj['cp'])
			if validIV(obj):
				stri += ' L{}'.format(obj['level'])
			discordStrArray.append(stri + ')')
		discordStrArray += [
			'until',
			getTimeString(obj['despawn']),
			'(' + getTimeDifferenceString(obj['despawn']) + ').'
		]
		addr = getAddress(obj['lat'], obj['lng'])
		if addr is not None:
			discordStrArray.append(addr + '.')
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

def getPokemonName(pID):
	if len(POKEMON_NAMES) >= pID:
		return POKEMON_NAMES[pID - 1]
	else:
		return 'PokemonID: {}'.format(pID)
		
def getPokemonNameFromObj(pok):
	formName = ''
	if 'form' in pok and pok['form'] != '0' and pok['form'] != '-1':
		if pok['pokemon_id'] == '201':
			formName = ' - {}'.format(chr(int(pok['form']) + 64))
		elif pok['form'] == '80':
			formName = ' Alolan'
	return getPokemonName(int(pok['pokemon_id'])) + formName

def getTimeString(utcTime):
	tz = pytz.timezone('Australia/Sydney')
	return datetime.datetime.fromtimestamp(int(utcTime), tz).strftime('%H:%M:%S')

def getTimeDifferenceString(utcTime):
	mins, secs = divmod((datetime.datetime.fromtimestamp(int(utcTime)) - datetime.datetime.now()).total_seconds(), 60)
	return '{}m{}s'.format(int(mins), int(math.floor(secs)))

def getURL():
	return 'https://sydneypogomap.com/query2.php?since=0&mons={}&bounds={}'.format(','.join(str(x) for x in range(1, MAX_MON_ID)), ','.join(str(x) for x in POKEMON_AREA))

def isDespawned(spawn):
	endTime = None
	if 'despawn' in spawn:
		endTime = int(spawn['despawn'])
	elif spawn['pokemon_id'] == '0':
		endTime = int(spawn['raid_start'])
	else:
		endTime = int(spawn['raid_end'])
	return datetime.datetime.now() > datetime.datetime.fromtimestamp(endTime)

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
	rlat = Decimal(raid['lat'])
	rlng = Decimal(raid['lng'])
	return rlat >= RAID_AREA['S'] and rlat <= RAID_AREA['N'] and rlng >= RAID_AREA['W'] and rlng <= RAID_AREA['E']

def isRare(pok):
	return int(pok['pokemon_id']) in POKEMON

def parseResponse(res):
	# can't get brotli working on GAE
	# ImportError: dynamic module does not define init function (init_brotli)
	''' if res.headers['Content-Encoding'] == 'br':
		return json.loads(brotli.decompress(res.content))
	else: '''
	return res.json()

def postDiscord(type, obj):
	response = requests.post(
		headers = { 'Content-Type':  'application/json' },
		url = WEBHOOKS[type],
		data = '{"content":"' + getDiscordString(type, obj) + '"}'
	)

def validIV(pok):
	return pok['attack'] != '-1' and pok['defence'] != '-1' and pok['stamina'] != '-1'

class Clear(webapp2.RequestHandler):
	def get(self):
		global SEEN_LIST
		global SEEN_RAID_LIST
		upperBound = int(time.time()) - 600 # 10 min buffer
		for pok in SEEN_LIST:
			endTime = int(pok['despawn'])
			if endTime < upperBound:
				SEEN_LIST.remove(pok)
		for raid in SEEN_RAID_LIST:
			endTime = int(raid['raid_end']) - 600
			if endTime < upperBound:
				SEEN_RAID_LIST.remove(raid)

class Pokemon(webapp2.RequestHandler):
	def get(self):
		global SEEN_LIST
		''' if LATEST_ETAG is None:
			return '''
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
				if isRare(pok):
					postDiscord(Scan.RARE_MON, pok)
				if isPerfectIV(pok):
					postDiscord(Scan.PERFECT_MON, pok)
				if isHighIV(pok):
					postDiscord(Scan.HIGH_MON, pok)

class Raids(webapp2.RequestHandler):
	def get(self):
		global SEEN_RAID_LIST
		''' if LATEST_ETAG is None:
			return '''
		response = requests.get(
			url = 'https://sydneypogomap.com/raids.php',
			headers = getHeaders('https://sydneypogomap.com/gym.html')
		)
		raidList = parseResponse(response)
		if 'raids' not in raidList:
			return
		for raid in raidList['raids']:
			if not raid in SEEN_RAID_LIST and not isDespawned(raid):
				SEEN_RAID_LIST.append(raid)
				if isRaidValuable(raid) and isRaidWithinBoundaries(raid):
					postDiscord(Scan.RAID, raid)

""" class Update(webapp2.RequestHandler):
	# Options for this
	# 1. Have a python file so you can have pokemon ID and name comment and parse it with eval but that's nasty and possibly insecure?
	# 2. Have a json filled with only names and parse it here turning it into an object the code can work with (json cant have comments)
	# I went with 2 because it seems like the better option
	def get(self):
		global POKEMON
		global RAIDS
		global LATEST_ETAG
		response = requests.get( url = FILTER_URL )
		if 'ETag' not in response.headers or LATEST_ETAG == response.headers['ETag']:
			# if not changed since last time then dont bother
			return
		resObj = response.json()
		monObj = {}
		for mon in resObj['pokemon']:
			pID = POKEMON_NAMES.index(mon)
			if pID != -1:
				monObj[str(pID + 1)] = resObj['pokemon'][mon]
		POKEMON = monObj
		raidObj = {}
		for raid in resObj['raids']:
			if resObj['raids'][raid] is None:
				raidObj[raid] = None
			else:
				raidObj[raid] = []
				for mon in resObj['raids'][raid]:
					pID = POKEMON_NAMES.index(mon)
					if pID != -1:
						raidObj[raid].append(str(pID + 1))
		RAIDS = raidObj
		MAX_MON_ID = findMaxMonID()
		LATEST_ETAG = response.headers['ETag'] """

app = webapp2.WSGIApplication([
	('/clear', Clear),
	('/raids', Raids),
	('/mon', Pokemon),
#	('/update', Update)
])
