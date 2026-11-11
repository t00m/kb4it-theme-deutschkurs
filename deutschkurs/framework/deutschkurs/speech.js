// deutschkurs: Listen buttons with the browser's speech synthesis.
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});

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

  function init(doc) {
    var body = doc.body;
    var data = body.dataset || {};
    var synth = root.speechSynthesis;
    var voice = null;

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

    // Speak a text; me picks voice_me. Returns false when there is no German voice.
    function say(text, me) {
      if (!voice || !text) return false;
      var chosen = pickFor(synth.getVoices(), data.speechLang || "de-DE", data.voice || null, data.voiceMe || "", me) || voice;
      var utterance = new root.SpeechSynthesisUtterance(text);
      utterance.voice = chosen;
      utterance.lang = chosen.lang;
      synth.cancel();
      synth.speak(utterance);
      return true;
    }
    dk.speech.say = say;

    doc.addEventListener("click", function (event) {
      var button = event.target && event.target.closest ? event.target.closest(".dk-listen") : null;
      if (!button) return;
      say(button.getAttribute("data-say"), button.getAttribute("data-me") === "true");
    });
  }

  dk.speech = { pickVoice: pickVoice, pickFor: pickFor, init: init, say: function () { return false; } };

  if (root.document && root.document.addEventListener) {
    root.document.addEventListener("DOMContentLoaded", function () { init(root.document); });
  }
})(typeof window !== "undefined" ? window : this);
