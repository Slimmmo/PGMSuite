// ==UserScript===
// @name         PGMSuite
// @homepage     https://github.com/Slimmmo/PGMSuite/
// @namespace    PGMSuite
// @version      1
// @include      https://*pogomap.com/*
// @grant        none
// ==/UserScript==

function indexOfPokemons(pokemon, pokemons) {
	if (!showPokemon(pokemon)) {
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

function showPokemon(p) {
	var iv = (p.attack + p.defence + p.stamina) / 0.45;
	if (document.getElementById('iv_' + p.id).value !== '') {
		return iv > document.getElementById('iv_' + p.id).value;
	} else if (document.getElementById('fcb').checked || !isPokemonChecked(p.id)) {
		return iv > document.getElementById('iiv').value;
	} else {
		return true;
	}
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

function saveIVEverything() {
	localStorage.setItem('iv_everything', document.getElementById('fcb').checked);
}

function saveIVValue() {
	localStorage.setItem('iv_value', document.getElementById('iiv').value);
}

function saveWebhook() {
	localStorage.setItem('whURL', document.getElementById('iwh').value);
}

function updateIV(val) {
	localStorage.setItem('iv_' + val, document.getElementById('iv_' + val).value);
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
	iiv.value = localStorage.getItem('iv_value') || 82;
	iiv.onchange = saveIVValue;
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
	fcb.onchange = saveIVEverything;
	fcb.checked = localStorage.getItem('iv_everything') || false;
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
	
	var filter = document.getElementById('filter_list_top').getElementsByClassName('filter_checkbox');
	for (var i = 0; i < filter.length; i++) {
		var disabled = filter[i].classList.contains('input_disabled') ? ' disabled ' : '';
		var pid = filter[i].firstChild.value;
		var ivSet = localStorage.getItem('iv_' + pid) !== '';
		var ivString = ivSet ? ' value="' + localStorage.getItem('iv_' + pid) + '"' : '';
		var inp = document.createElement('input');
		inp.type = 'number';
		inp.id = 'iv_' + pid;
		inp.value = ivSet ? localStorage.getItem('iv_' + pid) : '';
		if (filter[i].classList.contains('input_disabled')) {
			inp.disabled = 'true';
		}
		inp.style = 'margin-left: 3px; max-width: 45px; display: inline-block;';
		inp.setAttribute('onchange', 'updateIV(' + pid + ')');
		filter[i].append(inp);
	}
	
	document.getElementById('map').style.top = '';
	document.getElementById('map').style.bottom = '';
	document.getElementById('filter_settings').style.top = '50px';
	document.getElementById('locate').style.top = '50px';
};

// Inject this code into the site's code

modifyHTML();
addJS_Node (indexOfPokemons);
addJS_Node (showPokemon);
addJS_Node (postDiscord);
addJS_Node (saveIVEverything);
addJS_Node (saveIVValue);
addJS_Node (saveWebhook);
addJS_Node (updateIV);

function addJS_Node (text, s_URL, funcToRun, runOnLoad) {
	var D								   = document;
	var scriptNode						  = D.createElement ('script');
	if (runOnLoad) {
		scriptNode.addEventListener ("load", runOnLoad, false);
	}
	scriptNode.type						 = "text/javascript";
	if (text)	   scriptNode.textContent  = text;
	if (s_URL)	  scriptNode.src		  = s_URL;
	if (funcToRun)  scriptNode.textContent  = '(' + funcToRun.toString() + ')()';

	var targ = D.getElementsByTagName ('head')[0] || D.body || D.documentElement;
	targ.appendChild (scriptNode);
}
