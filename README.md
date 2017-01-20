# PGMSuite
\*pogomap site enhancements

# What it does
1. Adds support to filter IVs in a very basic way.
2. Adds support to post to Discord when it sees a new Pokemon.

WARNING: If Discord posts are enabled it will post every Pokemon it sees to Discord! This will quickly become overwhelming if filters are turned off on the site and the IV filters are too low.

# How to use
## Basic Setup
1. Download [PGMSuite.js](https://raw.githubusercontent.com/Slimmmo/PGMSuite/master/PGMSuite.js)
2. If you wish to use the Discord notifications, change Line 27 to use your Discord webhook URL. See more about webhooks [here](https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks).
If you do not wish to use the Discord notifications, change line 22 to `\\postDiscord(pokemon);`
3. Install a userscript manager if you do not already have one.
My recommendations: 
[TamperMonkey for Chrome](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=en)
[GreaseMonkey for Firefox](https://addons.mozilla.org/en-US/firefox/addon/greasemonkey/)
4. Load PGMSuite.js
5. Refresh the pogomap site.

## How to modify IV Filtering

Line 11 : `if ((false || !isPokemonChecked(pokemon.id)) &&`

The `false` means it will not apply the IV filter to any Pokemon checked in the filters list.

Change this to `true` to apply the filters to everything.


Line 12 : `(pokemon.attack + pokemon.defence + pokemon.stamina) / 0.45 < 82) {`

Means anything over 82% IVs (top tier appraisals) will be shown. Changing the 82 to any number will work.

To get it to show all pokemon change the number to -7 or more negative (-8 etc).
