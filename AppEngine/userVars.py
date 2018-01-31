RAID_AREA = {
	'N': -33.915349,
	'E': 151.236956,
	'S': -33.919713,
	'W': 151.225326
}
RAIDS = {
	4: [
    248, # Tyranitar
    306 # Aggron
  ],
	5: None
}
GYM_NAMES = {
	'-33.917501151.226467': 'Tyree Building',
	'-33.918655151.226832': 'New College',
	'-33.919704151.226648': 'BP/Maccas',
	'-33.918366151.23053': 'Naked Lady',
	'-33.917983151.231283': 'Metal Ball',
	'-33.916805151.233311': 'Library Lawn',
	'-33.916831151.233777': 'Nelson Mandela Bust (Library Lawn)',
	'-33.916666151.235': 'Gate 9',
	'-33.91795151.234829': 'Museum of Human Disease'
}
POKEMON_AREA = [
	151.214829, # W
	151.241834, # E
	-33.926011, # S
	-33.911816, # N
]
# A value of 'None' means every spawn will be sent to Discord
# The idea was to to be able to set a number and it will only send if IV% > number, currently not implemented
# Every 100% IV will be sent even if the pokemon is not in this list
POKEMON = {
  # GEN 1
  3: None, # Venusaur
  6: None, # Charizard
  9: None, # Blastoise
	26: None, # Raichu
	59: None, # Arcanine
	65: None, # Alakazam
	68: None, # Machamp
  76: None, # Golem
  89: None, # Muk
  94: None, # Gengar
  112: None, # Rhydon
	113: None, # Chansey
	130: None, # Gyarados
	131: None, # Lapras
	137: None, # Porygon
	142: None, # Aerodactyl
	143: None, # Snorlax
	144: None, # Articuno
	145: None, # Zapdos
	146: None, # Moltres
  148: None, # Dragonair
	149: None, # Dragonite
	150: None, # Mewtwo
	151: None, # Mew
  # GEN 2
  154: None, # Meganium
  157: None, # Typhlosion
  160: None, # Feraligatr
  176: None, # Togetic
	179: None, # Mareep
  180: None, # Flaaffy
	181: None, # Ampharos
	201: None, # Unown
	232: None, # Donphan
	242: None, # Blissey
	243: None, # Raikou
	244: None, # Entei
	245: None, # Suicune
	246: None, # Larvitar
	247: None, # Pupitar
	248: None, # Tyranitar
	249: None, # Lugia
	250: None, # Ho-Oh
	251: None, # Celebi
  # GEN 3
  254: None, # Sceptile
  256: None, # Combusken
  257: None, # Blaziken
  260: None, # Swampert
  267: None, # Beautifly
  269: None, # Dustox
  272: None, # Ludicolo
  275: None, # Shiftry
  281: None, # Kirlia
  282: None, # Gardevoir
  288: None, # Vigoroth
  289: None, # Slaking
  295: None, # Exploud
  305: None, # Lairon
  306: None, # Aggron
  308: None, # Medicham
  319: None, # Sharpedo
  321: None, # Wailord
  342: None, # Crawdaunt
  344: None, # Claydol
  349: None, # Feebas
  350: None, # Milotic
  365: None, # Walrein
  372: None, # Shelgon
  373: None, # Salamence
  375: None, # Metang
  376: None, # Metagross
  377: None, # Regirock
  378: None, # Regice
  379: None, # Registeel
  380: None, # Latias
  381: None, # Latios
  382: None, # Kyogre
  383: None, # Groudon
  384: None, # Rayquaza
  385: None, # Jirachi
  386: None # Deoxys
}
