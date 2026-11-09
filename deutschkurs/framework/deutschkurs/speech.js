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

  function init(doc) {
    var body = doc.body;
    var data = body.dataset || {};
    var synth = root.speechSynthesis;
    var voice = null;

    function apply() {
      voice = data.speech === "false" || !synth ? null : pickVoice(synth.getVoices(), data.speechLang || "de-DE", data.voice || null);
      if (voice) body.classList.remove("dk-no-voice");
      else body.classList.add("dk-no-voice");
    }

    apply();
    if (synth && synth.addEventListener) synth.addEventListener("voiceschanged", apply);

    doc.addEventListener("click", function (event) {
      var button = event.target && event.target.closest ? event.target.closest(".dk-listen") : null;
      if (!button || !voice) return;
      var utterance = new root.SpeechSynthesisUtterance(button.getAttribute("data-say"));
      utterance.voice = voice;
      utterance.lang = voice.lang;
      synth.cancel();
      synth.speak(utterance);
    });
  }

  dk.speech = { pickVoice: pickVoice, init: init };

  if (root.document && root.document.addEventListener) {
    root.document.addEventListener("DOMContentLoaded", function () { init(root.document); });
  }
})(typeof window !== "undefined" ? window : this);
