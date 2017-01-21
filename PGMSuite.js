// ==UserScript==
// @name         PGMSuite
// @homepage     https://github.com/Slimmmo/PGMSuite/
// @namespace    PGMSuite
// @version      1
// @include      https://*pogomap.com/*
// @grant        none
// ==/UserScript==

function indexOfPokemons(pokemon, pokemons) {
    if ((false || !isPokemonChecked(pokemon.id)) &&
       (pokemon.attack + pokemon.defence + pokemon.stamina) / 0.45 < 82) {
        return 0;
    } else {
        for (var i = 0; i < pokemons.length; ++i) {
            var currentPokemon = pokemons[i];
            if (pokemon.isEqual(currentPokemon)) {
                return i;
            }
        }
    }
    if (document.getElementById('cb').checked) {
        postDiscord(pokemon);
    }
    return -1;
}

function postDiscord(p) {
    var webhookURL = ' INSERT DISCORD WEBHOOK HERE ';
    var date = new Date(p.despawn * 1000);
    var seconds = "0" + date.getSeconds();
    var dateString = date.getHours() + ':' + ("0" + date.getMinutes()).substr(-2) + ':' + ("0" + date.getSeconds()).substr(-2);
    var text = getPokemonName(p) + ' ' + Math.floor((p.attack + p.defence + p.stamina) / 0.45) +
        '% with ' + getMoveName(p.move1) + ', ' + getMoveName(p.move2) + ' until ' + dateString +
        ' at http://maps.google.com/maps?q=' + p.center.lat + ',' + p.center.lng + '&zoom=14';
    $.ajax({
        data: 'content=' + text,
        dataType: 'json',
        processData: false,
        type: 'POST',
        url: webhookURL
    });
}

var cb = document.createElement('input');
cb.type = 'checkbox';
cb.id = 'cb';
var lab = document.createElement('label');
lab.htmlFor = 'cb';
lab.appendChild(document.createTextNode('Enable Discord'));

// Inject this code into the site's code

document.getElementById('topbar').appendChild(cb);
document.getElementById('topbar').appendChild(lab);
addJS_Node (indexOfPokemons);
addJS_Node (postDiscord);

function addJS_Node (text, s_URL, funcToRun, runOnLoad) {
    var D                                   = document;
    var scriptNode                          = D.createElement ('script');
    if (runOnLoad) {
        scriptNode.addEventListener ("load", runOnLoad, false);
    }
    scriptNode.type                         = "text/javascript";
    if (text)       scriptNode.textContent  = text;
    if (s_URL)      scriptNode.src          = s_URL;
    if (funcToRun)  scriptNode.textContent  = '(' + funcToRun.toString() + ')()';

    var targ = D.getElementsByTagName ('head')[0] || D.body || D.documentElement;
    targ.appendChild (scriptNode);
}
