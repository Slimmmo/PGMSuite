// ==UserScript==
// @name         PGMSuite
// @homepage     https://github.com/Slimmmo/PGMSuite/
// @namespace    PGMSuite
// @version      1
// @include      https://*pogomap.com/*
// @grant        none
// ==/UserScript==

function indexOfPokemons(pokemon, pokemons) {
    if ((document.getElementById('fcb').checked || !isPokemonChecked(pokemon.id)) &&
       (pokemon.attack + pokemon.defence + pokemon.stamina) / 0.45 < document.getElementById('iiv').value) {
        return 0;
    } else {
        for (var i = 0; i < pokemons.length; ++i) {
            var currentPokemon = pokemons[i];
            if (pokemon.isEqual(currentPokemon)) {
                return i;
            }
        }
    }
    if (document.getElementById('icb').checked) {
       postDiscord(pokemon);
    }
    return -1;
}

function postDiscord(p) {
    var webhookURL = document.getElementById('iwh').value;
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

function saveWebhook() {
    localStorage.setItem('whURL', document.getElementById('iwh').value);
}

function modifyHTML() {
    var icb = document.createElement('input');
    icb.type = 'checkbox';
    icb.id = 'icb';
    var clab = document.createElement('label');
    clab.htmlFor = 'icb';
    clab.appendChild(document.createTextNode('Enable Discord'));
    clab.style.cssText = 'padding-right: 7px';
    document.getElementById('topbar').appendChild(icb);
    document.getElementById('topbar').appendChild(clab);
    
    var iiv = document.createElement('input');
    iiv.type = 'number';
    iiv.id = 'iiv';
    iiv.max = 100;
    iiv.value = 82;
    iiv.style.cssText = 'max-width: 45px';
    var nlab = document.createElement('label');
    nlab.htmlFor = 'iiv';
    nlab.appendChild(document.createTextNode('IV %'));
    nlab.style.cssText = 'padding-right: 7px';
    document.getElementById('topbar').appendChild(iiv);
    document.getElementById('topbar').appendChild(nlab);
    
    var fcb = document.createElement('input');
    fcb.type = 'checkbox';
    fcb.id = 'fcb';
    var flab = document.createElement('label');
    flab.htmlFor = 'fcb';
    flab.appendChild(document.createTextNode('IV filter everything'));
    flab.style.cssText = 'padding-right: 7px';
    document.getElementById('topbar').appendChild(fcb);
    document.getElementById('topbar').appendChild(flab);
    
    var iwh = document.createElement('input');
    iwh.type = 'text';
    iwh.id = 'iwh';
    iwh.onchange = saveWebhook;
    iwh.value = localStorage.getItem('whURL') || '';
    iwh.style.cssText = 'max-width: 50px';
    var wlab = document.createElement('label');
    wlab.htmlFor = 'iwh';
    wlab.appendChild(document.createTextNode('Webhook URL'));
    document.getElementById('topbar').appendChild(iwh);
    document.getElementById('topbar').appendChild(wlab);
};

// Inject this code into the site's code

modifyHTML();
addJS_Node (indexOfPokemons);
addJS_Node (postDiscord);
addJS_Node (saveWebhook);

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
