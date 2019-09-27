
# just gets the moves and their IDs

import json, re

MOVE_REGEX = re.compile(r'^COMBAT_V(\d+)_MOVE_(.*)$')
firstLine = True

with open('GAME_MASTER-1570842289498.json', 'r') as f:
	GM = json.load(f)
	with open('moves.out', 'w+') as f2:
		f2.write('MOVE_NAMES = {\r\n')

		for template in GM['itemTemplates']:
			result = MOVE_REGEX.match(template['templateId'])
			if result != None:
				id = int(result.group(1))
				name = result.group(2)
				name = name.replace('_', ' ').title()
				if name.endswith(' Fast') or name.endswith(' Fast Blastoise'):
					name = name.split(' Fast')[0]
				f2.write(('' if firstLine else ',\r\n') + "\t%d: '%s'" % (id, name))
				firstLine = False
		f2.write('\r\n}')