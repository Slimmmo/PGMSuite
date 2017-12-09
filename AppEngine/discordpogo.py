import datetime, sys, time, webapp2
sys.path.append('lib')
import requests
from enum import Enum
from constants import *
from userVars import *

seenList = []
seenRaidList = []

class Scan(Enum):
	RAID = 0
	RARE_MON = 1
	HIGH_MON = 2

def getDiscordString(type, obj):
	discordStrArray = []
	if type == Scan.RAID:
		if obj['pokemon_id'] == 0:
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
			if obj['move1'] != 0 and obj['move2'] != 0:
				discordStrArray.append(getMoveName(obj['move1']) + ', ' + getMoveName(obj['move2']) + '.')
	else:
		discordStrArray.append(getPokemonNameFromObj(obj))
		if validIV(obj):
			discordStrArray.append(getIVPercentage(obj))
		if obj['cp'] != -1:
			str = '({} CP'.format(obj['cp'])
			if validIV(obj):
				# obj['level'] has not been trustworthy so figure it out ourselves
				# don't figure it out just to test other things first
				str += ' L{}'.format(obj['level'])
			discordStrArray.append(str + ')')
		discordStrArray += [
			'until',
			getTimeString(obj['despawn']),
			'at',
			getGoogleMapsURL(obj['lat'], obj['lng'])
		]
	return ' '.join(discordStrArray)

def getGoogleMapsURL(lat, lng):
	return 'http://maps.google.com/maps?q={},{}'.format(lat, lng)

def getIVPercentage(pok):
	return int(round(pok['attack'] + pok['defence'] + pok['stamina']) / 0.45, 0)

def getLocationName(obj):
	key = '{}{}'.format(obj['lat'], obj['lng'])
	if key in GYM_NAMES:
		return GYM_NAMES[key]
	else:
		return '{},{}'.format(obj['lat'], obj['lng'])

def getMoveName(mID):
	return MOVE_NAMES[mID]

def getPokemonName(pID):
	return POKEMON_NAMES[pID]
		
def getPokemonNameFromObj(pok):
	return getPokemonName(pok['pokemon_id']) + '' if pok['form'] == 0 else ' - {}'.format(pok['form']) # TODO: what is this for unown?

def getTimeString(utcTime):
	return datetime.datetime.fromtimestamp(int(utcTime)).strftime('%H:%M:%S')

def getURL():
	return 'https://sydneypogomap.com/query2.php?since=0&mons={}&bounds={}'.format(','.join(POKEMON.keys()), POKEMON_AREA)

def isHighIV(pok):
	if pok['pokemon_id'] in POKEMON:
		if POKEMON[pok['pokemon_id']] is not None and validIV(pok):
			return getIVPercentage(pok) >= POKEMON[pok['pokemon_id']]
	return False

def isRaidValuable(raid):
	return raid['level'] in RAIDS and (RAIDS[raid['level']] == None or raid['pokemon_id'] in RAIDS[raid['level']])

def isRaidWithinBoundaries(raid):
	# TODO: currently only works with rectangles that dont go over the lat/lng boundaries where the sign flips
	return raid['lat'] >= RAID_AREA['W'] and raid['lat'] <= RAID_AREA['W'] and raid['lng'] >= RAID_AREA['S'] and raid['lng'] <= RAID_AREA['N']

def isRare(pok):
	if pok['pokemon_id'] in POKEMON:
		return True

def postDiscord(type, obj):
	response = requests.post(
		url = WEBHOOKS[type],
		data = 'content=' + getDiscordString(type, obj)
	)

def validIV(pok):
	return pok['attack'] != -1 and pok['defence'] != -1 and pok['stamina'] != -1

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
		print('running mon')
		response = requests.get(
			url = getUrl(),
			headers = { 'Referer': 'https://sydneypogomap.com/?forcerefresh' }
		)
		monList = response.json()
		if 'pokemons' not in monList:
			return
		for pok in monList['pokemons']:
			if not pok in seenList:
				seenList.append(pok)
				if isRare(pok):
					postDiscord(Scan.RARE_MON, pok)
				if isHighIV(pok):
					postDiscord(Scan.HIGH_MON, pok)

class Raids(webapp2.RequestHandler):
	def get(self):
		global seenRaidList
		response = requests.get(
			url = 'https://sydneypogomap.com/raids.php',
			headers = { 'Referer': 'https://sydneypogomap.com/gym.html' }
		)
		raidList = response.json()
		if 'raids' not in raidList:
			return
		print(raidList)
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