const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const SOURCE = fs.readFileSync(
  path.join(__dirname, "..", "..", "deutschkurs", "framework", "deutschkurs", "speech.js"), "utf8");

function load(extra) {
  const context = Object.assign({}, extra);
  vm.runInNewContext(SOURCE, context);
  return context;
}

const VOICES = [
  { name: "English", lang: "en-US" },
  { name: "Anna", lang: "de-AT" },
  { name: "Markus", lang: "de-DE" },
];

test("pickVoice prefers the named voice", () => {
  const { pickVoice } = load().Deutschkurs.speech;
  assert.strictEqual(pickVoice(VOICES, "de-DE", "Anna").name, "Anna");
});

test("pickVoice falls back to the exact language", () => {
  const { pickVoice } = load().Deutschkurs.speech;
  assert.strictEqual(pickVoice(VOICES, "de-DE", null).name, "Markus");
});

test("pickVoice falls back to any German voice", () => {
  const { pickVoice } = load().Deutschkurs.speech;
  assert.strictEqual(pickVoice(VOICES.slice(0, 2), "de-DE", null).name, "Anna");
});

test("pickVoice returns null without a German voice", () => {
  const { pickVoice } = load().Deutschkurs.speech;
  assert.strictEqual(pickVoice([{ name: "x", lang: "en-US" }], "de-DE", null), null);
});

function fakeDocument(speech) {
  const classes = new Set();
  return {
    classes,
    body: {
      dataset: { speech: speech, speechLang: "de-DE", voice: "" },
      classList: { add: (c) => classes.add(c), remove: (c) => classes.delete(c) },
    },
    addEventListener() {},
  };
}

test("init without a German voice marks the body and does not throw", () => {
  const synth = { getVoices: () => [{ name: "x", lang: "en-US" }], addEventListener() {} };
  const ctx = load({ speechSynthesis: synth });
  const doc = fakeDocument("true");
  ctx.Deutschkurs.speech.init(doc);
  assert.ok(doc.classes.has("dk-no-voice"));
});

test("init without speechSynthesis marks the body", () => {
  const ctx = load();
  const doc = fakeDocument("true");
  ctx.Deutschkurs.speech.init(doc);
  assert.ok(doc.classes.has("dk-no-voice"));
});

test("init with a German voice leaves the buttons on", () => {
  const synth = { getVoices: () => VOICES, addEventListener() {} };
  const ctx = load({ speechSynthesis: synth });
  const doc = fakeDocument("true");
  ctx.Deutschkurs.speech.init(doc);
  assert.ok(!doc.classes.has("dk-no-voice"));
});


test("init with speech off hides buttons without the no-voice note", () => {
  const synth = { getVoices: () => VOICES, addEventListener() {} };
  const ctx = load({ speechSynthesis: synth });
  const doc = fakeDocument("false");
  ctx.Deutschkurs.speech.init(doc);
  assert.ok(doc.classes.has("dk-speech-off"));
  assert.ok(!doc.classes.has("dk-no-voice"));
});

test("my turns use voice_me, other turns the main voice", () => {
  const { pickFor } = load().Deutschkurs.speech;
  assert.strictEqual(pickFor(VOICES, "de-DE", "Markus", "Anna", true).name, "Anna");
  assert.strictEqual(pickFor(VOICES, "de-DE", "Markus", "Anna", false).name, "Markus");
  assert.strictEqual(pickFor(VOICES, "de-DE", "Markus", "", true).name, "Markus");
});

test("normalise reads times, amounts, abbreviations and dates", () => {
  const { normalise } = load().Deutschkurs.speech;
  assert.strictEqual(normalise("Um 8:00 Uhr"), "Um acht Uhr");
  assert.strictEqual(normalise("Um 14:30 Uhr"), "Um vierzehn Uhr dreißig");
  assert.strictEqual(normalise("ab 10:05 Uhr"), "ab zehn Uhr fünf");
  assert.strictEqual(normalise("Das kostet 5 €."), "Das kostet fünf Euro.");
  assert.strictEqual(normalise("nur 0,99 €"), "nur null Euro neunundneunzig");
  assert.strictEqual(normalise("5,50 EUR"), "fünf Euro fünfzig");
  assert.strictEqual(normalise("€ 21"), "einundzwanzig Euro");
  assert.strictEqual(normalise("z. B. Obst, d. h. Äpfel usw."), "zum Beispiel Obst, das heißt Äpfel und so weiter");
  assert.strictEqual(normalise("am 3.11. kommt"), "am dritten November kommt");
  assert.strictEqual(normalise("bis zum 1. März"), "bis zum ersten März");
  assert.strictEqual(normalise("Heute ist der 7.10.2026"), "Heute ist der siebte Oktober 2026");
});

test("normalise leaves text without numbers unchanged", () => {
  const { normalise } = load().Deutschkurs.speech;
  for (const text of ["Guten Morgen!", "", "Ich habe 3 Kinder.", "Zimmer 12"]) {
    assert.strictEqual(normalise(text), text);
  }
});

test("numberWords writes German numbers", () => {
  const { numberWords } = load().Deutschkurs.speech;
  const cases = { 0: "null", 1: "eins", 7: "sieben", 11: "elf", 16: "sechzehn", 17: "siebzehn", 20: "zwanzig",
    21: "einundzwanzig", 30: "dreißig", 99: "neunundneunzig", 100: "hundert", 101: "hunderteins",
    345: "dreihundertfünfundvierzig", 1000: "tausend", 2026: "zweitausendsechsundzwanzig" };
  for (const [n, words] of Object.entries(cases)) assert.strictEqual(numberWords(Number(n)), words, n);
});

function speakingDocument(data) {
  return {
    body: { dataset: Object.assign({ speech: "true", speechLang: "de-DE", voice: "" }, data),
            classList: { add() {}, remove() {} } },
    addEventListener() {},
  };
}

function fakeSynth() {
  const spoken = [];
  return {
    spoken,
    getVoices: () => VOICES,
    addEventListener() {},
    cancel() { spoken.cancelled = (spoken.cancelled || 0) + 1; },
    speak(u) { spoken.push(u); },
  };
}

function Utterance(text) { this.text = text; }

test("say normalises and speaks slow at slow_rate", () => {
  const synth = fakeSynth();
  const ctx = load({ speechSynthesis: synth, SpeechSynthesisUtterance: Utterance });
  ctx.Deutschkurs.speech.init(speakingDocument({ slowRate: "0.6" }));
  ctx.Deutschkurs.speech.say("Um 8:00 Uhr", false, true);
  assert.strictEqual(synth.spoken[0].text, "Um acht Uhr");
  assert.strictEqual(synth.spoken[0].rate, 0.6);
  ctx.Deutschkurs.speech.say("Hallo", false, false);
  assert.strictEqual(synth.spoken[1].rate, 1);
});

test("slow rate falls back to 0.75", () => {
  const synth = fakeSynth();
  const ctx = load({ speechSynthesis: synth, SpeechSynthesisUtterance: Utterance });
  ctx.Deutschkurs.speech.init(speakingDocument({ slowRate: "nonsense" }));
  ctx.Deutschkurs.speech.say("Hallo", false, true);
  assert.strictEqual(synth.spoken[0].rate, 0.75);
});

test("sayAll speaks items one after another with their voices", () => {
  const synth = fakeSynth();
  const played = [];
  function Audio(src) { this.src = src; this.play = () => { played.push(src); return { catch() {} }; }; }
  const ctx = load({ speechSynthesis: synth, SpeechSynthesisUtterance: Utterance, Audio });
  ctx.Deutschkurs.speech.init(speakingDocument({ voice: "Markus", voiceMe: "Anna" }));
  ctx.Deutschkurs.speech.sayAll([{ text: "Hallo" }, { text: "Hi", me: true }, { audio: "a.m4a" }, { text: "Tschüss" }]);
  assert.strictEqual(synth.spoken.length, 1);
  assert.strictEqual(synth.spoken[0].voice.name, "Markus");
  synth.spoken[0].onend();
  assert.strictEqual(synth.spoken.length, 2);
  assert.strictEqual(synth.spoken[1].voice.name, "Anna");
  synth.spoken[1].onend();
  assert.deepStrictEqual(played, ["a.m4a"]);
  assert.strictEqual(synth.spoken.length, 2);
  ctx.Deutschkurs.speech.lastAudio().onended();
  assert.strictEqual(synth.spoken[2].text, "Tschüss");
});

test("a new say stops a running sayAll", () => {
  const synth = fakeSynth();
  const ctx = load({ speechSynthesis: synth, SpeechSynthesisUtterance: Utterance });
  ctx.Deutschkurs.speech.init(speakingDocument({}));
  ctx.Deutschkurs.speech.sayAll([{ text: "eins" }, { text: "zwei" }]);
  ctx.Deutschkurs.speech.say("drei");
  synth.spoken[0].onend();
  assert.deepStrictEqual(synth.spoken.map((u) => u.text), ["eins", "drei"]);
});
