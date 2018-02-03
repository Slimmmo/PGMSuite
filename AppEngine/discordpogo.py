import datetime, math, sys, time, webapp2, logging
sys.path.append('lib')
import googlemaps, pytz, requests
from decimal import Decimal
from enum import Enum
from constants import *
from userVars import *
from privateUserVars import *

gmaps = googlemaps.Client(key = GMAP_API_KEY)

seenList = []
seenRaidList = []

class Scan(Enum):
	RAID = 0
	RARE_MON = 1
	HIGH_MON = 2
	PERFECT_MON = 3

def getAddress(lat, lng):
	locWhitelist = [
		'establishment',
		'premise',
		'route',
		'street_number'
	]
	returnArr = []
	try:
		res = gmaps.reverse_geocode((lat, lng))
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
			discordStrArray += addr + '.'
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
		'Accept-Encoding': 'gzip, deflate, br',
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
	return getPokemonName(int(pok['pokemon_id'])) + '' if ('form' not in pok or pok['form'] == '0') else ' - {}'.format(chr(int(pok['form']) + 64))

def getTimeString(utcTime):
	tz = pytz.timezone('Australia/Sydney')
	return datetime.datetime.fromtimestamp(int(utcTime), tz).strftime('%H:%M:%S')

def getTimeDifferenceString(utcTime):
	mins, secs = divmod((datetime.datetime.fromtimestamp(int(utcTime)) - datetime.datetime.now()).total_seconds(), 60)
	return '{}m{}s'.format(int(mins), int(math.floor(secs)))

def getURL():
	return 'https://sydneypogomap.com/query2.php?since=0&mons={}&bounds={}'.format(','.join(str(x) for x in range(1, max(POKEMON.keys()) + 1)), ','.join(str(x) for x in POKEMON_AREA))

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

def postDiscord(type, obj):
	response = requests.post(
		url = WEBHOOKS[type.value],
		data = 'content=' + getDiscordString(type, obj)
	)

def validIV(pok):
	return pok['attack'] != '-1' and pok['defence'] != '-1' and pok['stamina'] != '-1'

class Clear(webapp2.RequestHandler):
	def get(self):
		global seenList
		global seenRaidList
		upperBound = int(time.time()) - 600 # 10 min buffer
		for pok in seenList:
			endTime = int(pok['despawn'])
			if endTime < upperBound:
				seenList.remove(pok)
		for raid in seenRaidList:
			endTime = int(raid['raid_end']) - 600
			if endTime < upperBound:
				seenRaidList.remove(raid)

class Pokemon(webapp2.RequestHandler):
	def get(self):
		global seenList
		response = requests.get(
			url = getURL(),
			headers = getHeaders('https://sydneypogomap.com/')
		)
		monList = response.json()
		logging.debug(monList)
		if 'pokemons' not in monList:
			return
		for pok in monList['pokemons']:
			if not pok in seenList:
				seenList.append(pok)
				if isRare(pok):
					postDiscord(Scan.RARE_MON, pok)
				if isPerfectIV(pok):
					postDiscord(Scan.PERFECT_MON, pok)
				if isHighIV(pok):
					postDiscord(Scan.HIGH_MON, pok)

class Raids(webapp2.RequestHandler):
	def get(self):
		global seenRaidList
		response = requests.get(
			url = 'https://sydneypogomap.com/raids.php',
			headers = getHeaders('https://sydneypogomap.com/gym.html')
		)
		raidList = response.json()
		if 'raids' not in raidList:
			return
		for raid in raidList['raids']:
			if not raid in seenRaidList:
				seenRaidList.append(raid)
				if isRaidValuable(raid) and isRaidWithinBoundaries(raid):
					postDiscord(Scan.RAID, raid)

app = webapp2.WSGIApplication([
	('/clear', Clear),
	('/raids', Raids),
	('/mon', Pokemon)
])
