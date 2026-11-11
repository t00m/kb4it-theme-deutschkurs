// deutschkurs: Listen buttons with the browser's speech synthesis, and recordings.
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});

  var UNITS = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf",
               "zwölf", "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn"];
  var TENS = ["", "", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"];
  var MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
                "November", "Dezember"];
  var ABBREVIATIONS = [
    [/\bz\.\s?B\./g, "zum Beispiel"], [/\bd\.\s?h\./g, "das heißt"], [/\busw\./g, "und so weiter"],
    [/\bbzw\./g, "beziehungsweise"], [/\bca\./g, "circa"], [/\bNr\./g, "Nummer"], [/\bTel\./g, "Telefon"],
  ];
  // Str. alone or at the end of a street name: Hauptstr. is Hauptstraße.
  var STREET = /(^|[^A-Za-zÄÖÜäöüß])([A-Za-zÄÖÜäöüß]*)([Ss])tr\./g;
  // Words before a date that take the dative ending: am dritten, bis zum ersten.
  var DATIVE = ["am", "vom", "zum", "dem"];
  var DEFAULT_SLOW = 0.75;

  // A whole number from 0 to 9999 in German words; other numbers stay digits.
  function numberWords(n) {
    if (n < 0 || n > 9999 || n !== Math.floor(n)) return String(n);
    if (n < 20) return UNITS[n];
    if (n < 100) {
      var one = n % 10;
      return (one ? (one === 1 ? "ein" : UNITS[one]) + "und" : "") + TENS[Math.floor(n / 10)];
    }
    var big = n < 1000 ? 100 : 1000;
    var head = Math.floor(n / big);
    var rest = n % big;
    var name = big === 100 ? "hundert" : "tausend";
    var lead = head === 1 ? "" : numberWords(head).replace(/eins$/, "ein");
    return lead + name + (rest ? numberWords(rest) : "");
  }

  // The ordinal of a day of the month: erste, dritte, zwanzigste; dative adds n.
  function ordinal(n, dative) {
    var word;
    if (n === 1) word = "erste";
    else if (n === 3) word = "dritte";
    else if (n === 7) word = "siebte";
    else if (n === 8) word = "achte";
    else if (n < 20) word = numberWords(n) + "te";
    else word = numberWords(n) + "ste";
    return dative ? word + "n" : word;
  }

  function dativeBefore(text, offset) {
    var before = text.slice(0, offset).trim().split(/\s+/);
    return DATIVE.indexOf(String(before[before.length - 1] || "").toLowerCase()) >= 0;
  }

  // An amount such as 1.200,50: whole euros with thousands dots, and one or two cent digits.
  function euros(whole, cents) {
    var amount = Number(whole.replace(/\./g, ""));
    var euro = amount === 1 ? "ein" : amount > 9999 ? String(amount) : numberWords(amount);
    var cent = cents ? Number(cents.length === 1 ? cents + "0" : cents) : 0;
    return euro + " Euro" + (cent ? " " + numberWords(cent) : "");
  }

  // Text as a German voice should read it: times, amounts, abbreviations and dates in words.
  function normalise(text) {
    var out = String(text || "");
    // An abbreviation at the end of the text also ended the sentence: keep that full stop.
    function expand(words) {
      return function (all) {
        var whole = arguments[arguments.length - 1], offset = arguments[arguments.length - 2];
        return words(arguments) + (offset + all.length === whole.length ? "." : "");
      };
    }
    function fixed(words) { return expand(function () { return words; }); }
    for (var i = 0; i < ABBREVIATIONS.length; i++) out = out.replace(ABBREVIATIONS[i][0], fixed(ABBREVIATIONS[i][1]));
    out = out.replace(STREET, expand(function (m) { return m[1] + m[2] + (m[3] === "S" ? "Straße" : "straße"); }));
    out = out.replace(/\b(\d{1,2})[:.](\d{2})\s*Uhr\b/g, function (all, h, m) {
      var hour = Number(h) === 1 ? "ein" : numberWords(Number(h));
      return hour + " Uhr" + (Number(m) ? " " + numberWords(Number(m)) : "");
    });
    out = out.replace(/\b(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d{1,2}))?\s*(?:€|EUR\b)/g, function (all, whole, cents) {
      return euros(whole, cents);
    });
    out = out.replace(/€\s*(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d{1,2}))?\b/g, function (all, whole, cents) {
      return euros(whole, cents);
    });
    // A date is not part of a longer dotted number such as 1.2.3.
    out = out.replace(/(?<![\d.])\b(\d{1,2})\.(\d{1,2})\.(\d{4}\b)?(?!\d|\.\d)/g, function (all, d, m, year, offset, whole) {
      var day = Number(d), month = Number(m);
      if (day < 1 || day > 31 || month < 1 || month > 12) return all;
      // A date without a year at the end of the text also ended the sentence: keep that full stop.
      var stop = !year && offset + all.length === whole.length ? "." : "";
      return ordinal(day, dativeBefore(whole, offset)) + " " + MONTHS[month - 1] + (year ? " " + year : "") + stop;
    });
    out = out.replace(new RegExp("\\b(\\d{1,2})\\.\\s+(" + MONTHS.join("|") + ")", "g"),
      function (all, d, month, offset, whole) {
        var day = Number(d);
        if (day < 1 || day > 31) return all;
        return ordinal(day, dativeBefore(whole, offset)) + " " + month;
      });
    return out;
  }

  // Named voice first, then the exact language, then any German voice.
  function pickVoice(voices, lang, name) {
    var list = voices || [];
    var i;
    if (name) {
      for (i = 0; i < list.length; i++) if (list[i].name === name) return list[i];
    }
    for (i = 0; i < list.length; i++) if (list[i].lang === lang) return list[i];
    for (i = 0; i < list.length; i++) if (String(list[i].lang).toLowerCase().indexOf("de") === 0) return list[i];
    return null;
  }

  // The voice of a turn: voice_me for the learner's own turns when it is set.
  function pickFor(voices, lang, name, meName, me) {
    return pickVoice(voices, lang, me && meName ? meName : name);
  }

  function slowRate(value) {
    var rate = parseFloat(value);
    return rate > 0 && rate <= 2 ? rate : DEFAULT_SLOW;
  }

  function init(doc) {
    var body = doc.body;
    var data = body.dataset || {};
    var synth = root.speechSynthesis;
    var voice = null;
    var slow = slowRate(data.slowRate);
    // Each say or sayAll gets a new token; a queue whose token is old stops.
    var token = 0;
    var audio = null;

    // Speech switched off in the settings: hide the buttons, no note about voices.
    if (data.speech === "false") {
      body.classList.add("dk-speech-off");
      return;
    }

    function apply() {
      voice = synth ? pickVoice(synth.getVoices(), data.speechLang || "de-DE", data.voice || null) : null;
      if (voice) body.classList.remove("dk-no-voice");
      else body.classList.add("dk-no-voice");
    }

    apply();
    if (synth && synth.addEventListener) synth.addEventListener("voiceschanged", apply);

    function stop() {
      token += 1;
      if (synth && synth.cancel) synth.cancel();
      if (audio && audio.pause) audio.pause();
      // Players on the page stop too, so two sounds never overlap.
      var players = doc.querySelectorAll ? doc.querySelectorAll("audio") : [];
      for (var i = 0; i < players.length; i++) if (players[i].pause) players[i].pause();
    }

    // A page player that starts stops the voice and any queue. The play event does not bubble: capture it.
    doc.addEventListener("play", function (event) {
      if (event.target === audio) return;
      token += 1;
      if (synth && synth.cancel) synth.cancel();
      if (audio && audio.pause) audio.pause();
    }, true);

    // Play one item {text, me, slow} or {audio}; call done when it ends. False when it cannot play.
    function play(item, done) {
      if (item.audio) {
        if (!root.Audio) return false;
        // A blocked play() rejects without an error event; a failed load does both. Advance once.
        var finished = false;
        var once = function () {
          if (finished) return;
          finished = true;
          done();
        };
        audio = new root.Audio(item.audio);
        audio.onended = once;
        audio.onerror = once;
        var started = audio.play();
        if (started && started.catch) started.catch(once);
        return true;
      }
      if (!voice || !item.text) return false;
      var chosen = pickFor(synth.getVoices(), data.speechLang || "de-DE", data.voice || null, data.voiceMe || "",
                           item.me) || voice;
      var utterance = new root.SpeechSynthesisUtterance(normalise(item.text));
      utterance.voice = chosen;
      utterance.lang = chosen.lang;
      utterance.rate = item.slow ? slow : 1;
      utterance.onend = done;
      utterance.onerror = done;
      synth.speak(utterance);
      return true;
    }

    // Speak a text now, stopping what plays; me picks voice_me. False when there is no German voice.
    function say(text, me, slowly) {
      stop();
      return play({ text: text, me: me, slow: slowly }, function () {});
    }

    // Play items one after another; a new say or sayAll stops the queue.
    function sayAll(items) {
      stop();
      var mine = token;
      var i = 0;
      function next() {
        while (mine === token && i < items.length) {
          if (play(items[i++], next)) return;
        }
      }
      next();
    }

    dk.speech.say = say;
    dk.speech.sayAll = sayAll;
    dk.speech.lastAudio = function () { return audio; };

    doc.addEventListener("click", function (event) {
      var target = event.target;
      var button = target && target.closest ? target.closest(".dk-listen, .dk-play-all") : null;
      if (!button) return;
      if (button.classList.contains("dk-play-all")) {
        sayAll(itemsIn(doc.querySelectorAll(button.getAttribute("data-play"))));
        return;
      }
      if (button.getAttribute("data-audio")) {
        sayAll([{ audio: button.getAttribute("data-audio") }]);
        return;
      }
      say(button.getAttribute("data-say"), button.getAttribute("data-me") === "true",
          button.getAttribute("data-rate") === "slow");
    });
  }

  // What Play all plays for each element: its recording, else the text of its first Listen button.
  function itemsIn(elements) {
    var items = [];
    for (var i = 0; i < elements.length; i++) {
      var recording = elements[i].querySelector("audio[src]");
      var button = elements[i].querySelector(".dk-listen[data-say]");
      if (recording) items.push({ audio: recording.getAttribute("src") });
      else if (button) items.push({ text: button.getAttribute("data-say"), me: button.getAttribute("data-me") === "true" });
    }
    return items;
  }

  dk.speech = { pickVoice: pickVoice, pickFor: pickFor, init: init, normalise: normalise, numberWords: numberWords,
                itemsIn: itemsIn, say: function () { return false; }, sayAll: function () {} };

  if (root.document && root.document.addEventListener) {
    root.document.addEventListener("DOMContentLoaded", function () { init(root.document); });
  }
})(typeof window !== "undefined" ? window : this);
