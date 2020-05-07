EARLIEST_RAID_TIME = '09:00' # 24 hour time, hours:minutes
RAID_AREA = {
	'N': -33.915349,
	'E': 151.236956,
	'S': -33.919713,
	'W': 151.225326
}
RAIDS = {
	4: [
		248, # Tyranitar
	],
	5: None # None means everything
}
GYM_NAMES = {
	'-33.917501151.226467': 'Tyree Building',
	'-33.918655151.226832': 'New College',
	'-33.919704151.226648': 'BP/Maccas',
	'-33.918366151.23053': 'Naked Lady',
	'-33.917983151.231283': 'Metal Ball',
	'-33.916805151.233311': 'Library Lawn',
	'-33.916831151.233777': 'Nelson Mandela Bust',
	'-33.916666151.235': 'Manu Et Mente',
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
# Every 90+% IV will be sent even if the pokemon is not in this list
POKEMON = {
	# GEN 1
	3: None, # Venusaur
	6: None, # Charizard
	9: None, # Blastoise
	26: None, # Raichu
	65: None, # Alakazam
	68: None, # Machamp
	76: None, # Golem
	89: None, # Muk
	94: None, # Gengar
	114: None, # Chansey
	130: None, # Gyarados
	131: None, # Lapras
	132: None, # Ditto
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
	176: None, # Togetic
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
	288: None, # Vigoroth
	289: None, # Slaking
	306: None, # Aggron
	321: None, # Wailord
	329: None, # Vibrava
	330: None, # Flygon
	358: None, # Chimecho
	365: None, # Walrein
	371: None, # Bagon
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
	386: None, # Deoxys
	# GEN 4
	389: None, # Torterra
	392: None, # Infernape
	395: None, # Empoleon
	409: None, # Rampardos
	443: None, # Gible
	444: None, # Gabite
	445: None, # Garchomp
	480: None, # Uxie
	481: None, # Mesprit
	482: None, # Azelf
	483: None, # Dialga
	484: None, # Palkia
	485: None, # Heatran
	486: None, # Regigigas
	487: None, # Giratina
	488: None, # Cresselia
	489: None, # Phione
	490: None, # Manaphy
	491: None, # Darkrai
	492: None, # Shaymin
	493: None, # Arceus
	# GEN 5
	# 494: None, # Victini ?
	497: None, # Serperior
	500: None, # Emboar
	503: None, # Samurott
	531: None, # Audino
	532: None, # Timburr
	533: None, # Gurdurr
	534: None, # Conkeldurr
	564: None, # Tirtouga
	565: None, # Carracosta
	566: None, # Archens
	567: None, # Archeops
	607: None, # Litwick
	608: None, # Lampent
	609: None, # Chandelure
	610: None, # Axew
	611: None, # Fraxure
	612: None, # Haxorus
	636: None, # Larvesta
	637: None, # Volcarona
	638: None, # Cobalion
	639: None, # Terrakion
	640: None, # Virizion
	641: None, # Tornadus
	642: None, # Thundurus
	643: None, # Reshiram
	644: None, # Zekrom
	645: None, # Landorus
	646: None, # Kyurem
	647: None, # Keldeo
	648: None, # Meloetta
	649: None # Genesect
}
EVENT_SPAWNS = {
}
MAX_MON_ID = 649