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

test("init with speech off marks the body", () => {
  const synth = { getVoices: () => VOICES, addEventListener() {} };
  const ctx = load({ speechSynthesis: synth });
  const doc = fakeDocument("false");
  ctx.Deutschkurs.speech.init(doc);
  assert.ok(doc.classes.has("dk-no-voice"));
});
