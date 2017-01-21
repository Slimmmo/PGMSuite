# PGMSuite
\*pogomap site enhancements

# What it does
1. Adds support to filter IVs in a very basic way.
2. Adds support to post to Discord when it sees a new Pokemon.

WARNING: If Discord posts are enabled it will post every Pokemon it sees to Discord! This will quickly become overwhelming if filters are turned off on the site and the IV filters are too low.

# How to use
## Basic Setup
1. Download [PGMSuite.js](https://raw.githubusercontent.com/Slimmmo/PGMSuite/master/PGMSuite.js)
2. If you wish to use the Discord notifications, change Line 27 to use your Discord webhook URL. See more about webhooks [here](https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks). The site will load with Discord notifications DISABLED so that the first load will not spam your channel unnecessarily. Once you have set-up the filters and 'watching area' to your liking, you can tick the checkbox up the top and Discord notifications will begin for newly appearing Pokemon.
3. Install a userscript manager if you do not already have one.
My recommendations: 
[TamperMonkey for Chrome](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=en)
[GreaseMonkey for Firefox](https://addons.mozilla.org/en-US/firefox/addon/greasemonkey/)
4. Load PGMSuite.js
5. Refresh the pogomap site.
