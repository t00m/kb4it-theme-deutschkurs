const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const DIR = path.join(__dirname, "..", "..", "deutschkurs", "framework", "deutschkurs");
const context = {};
for (const name of ["scheduler.js", "practice-core.js"]) {
  vm.runInNewContext(fs.readFileSync(path.join(DIR, name), "utf8"), context);
}
const { cards, view, session, counts } = context.Deutschkurs.practice;
const plain = (x) => JSON.parse(JSON.stringify(x));
const TODAY = "2026-11-11";

const SETTINGS = { learner_level: "A2", daily_reviews: 3, daily_new: 2, weekly_new: 4, prepare_days: 7, native: "en" };
function word(id, extra) {
  return Object.assign({ id: id, type: "Word", title: id, url: id + ".html", level: "A1", translation: "t-" + id,
    checked: "assistant", ready: true, situations: [], topics: [], date: "", forms: [id], examples: [],
    article: "der", plural: "none", plural_only: false, regional: [], noun: true }, extra || {});
}
const DATA = {
  settings: SETTINGS,
  situations: [{ title: "Elternabend", url: "e.html", next_time: "2026-11-14", cando: [0, 1] },
               { title: "Arzt", url: "a.html", next_time: "2026-12-30", cando: [0, 1] }],
  entries: [
    word("Termin", { plural: "die Termine", forms: ["Termin", "Termine"], date: "2026-11-01",
                     examples: [{ german: "Ich habe einen Termin.", translation: "I have an appointment." }] }),
    word("Eltern", { article: "", plural_only: true, situations: ["Elternabend"] }),
    word("Brotdose", { article: "die", regional: ["Brotbox"], date: "2026-11-05" }),
    word("neu", { noun: false, article: "", ready: true }),
    word("unfertig", { ready: false }),
    { id: "anrufen", type: "Verb", title: "anrufen", url: "anrufen.html", level: "A1", translation: "to call",
      checked: "assistant", ready: true, situations: [], topics: [], date: "", forms: ["anrufen", "rufe"],
      examples: [], participle: "angerufen", auxiliary: ["haben"],
      separable: [{ german: "Ich rufe dich an.", translation: "I call you.", parts: [[4, 8], [14, 16]] }] },
    { id: "fahren", type: "Verb", title: "fahren", url: "fahren.html", level: "A1", translation: "to drive",
      checked: "assistant", ready: true, situations: [], topics: [], date: "", forms: ["fahren"], examples: [],
      participle: "gefahren", auxiliary: ["haben", "sein"], separable: [] },
    { id: "talk", type: "Conversation", title: "Talk", url: "talk.html", level: "A1", translation: "",
      checked: "assistant", ready: true, situations: ["Elternabend"], topics: [], date: "",
      turns: [{ speaker: "A", german: "Hallo!", translation: "Hello!", me: false },
              { speaker: "ich", german: "Guten Tag.", translation: "Good day.", me: true }] },
    { id: "other", type: "Conversation", title: "Other", url: "other.html", level: "A1", translation: "",
      checked: "assistant", ready: true, situations: [], topics: [], date: "",
      turns: [{ speaker: "ich", german: "Ja.", translation: "Yes.", me: true }] },
    { id: "m1", type: "Mistake", title: "M", url: "m1.html", level: "A1", translation: "", checked: "assistant",
      ready: true, situations: [], topics: [], date: "", wrong: "Ich habe 40 Jahre.", right: "Ich bin 40 Jahre alt.",
      pattern: "es-tener" },
    { id: "g1", type: "Gap", title: "G", url: "g1.html", level: "", translation: "", checked: "assistant",
      ready: true, situations: [], topics: [], date: "", wanted: "I am ill.", german: "Ich bin krank." },
    { id: "g2", type: "Gap", title: "G2", url: "g2.html", level: "", translation: "", checked: "assistant",
      ready: true, situations: [], topics: [], date: "", wanted: "Later.", german: "" },
  ],
  sentences: [
    { entry: "Termin", doc: "brief", anchor: "s1", german: "Der Termin ist morgen.", translation: "a", start: 4, end: 10 },
    { entry: "Termin", doc: "talk", anchor: "t1", german: "Zwei Termine, bitte.", translation: "b", start: 5, end: 12 },
  ],
};
const ALL = cards(DATA);
const ids = (list) => plain(list.map((c) => c.id));

test("article card per noun but not plural only", () => {
  const article = ids(ALL.filter((c) => c.exercise === "article"));
  assert.deepStrictEqual(article.sort(), ["article:Brotdose", "article:Termin"]);
  const card = ALL.find((c) => c.id === "article:Termin");
  assert.deepStrictEqual(plain(card.choices), ["der", "die", "das"]);
  assert.strictEqual(card.answer, "der");
});

test("plural card needs a plural", () => {
  assert.deepStrictEqual(ids(ALL.filter((c) => c.exercise === "plural")), ["plural:Termin"]);
  assert.strictEqual(ALL.find((c) => c.id === "plural:Termin").answer, "die Termine");
});

test("to_target asks for the article and accepts regional words", () => {
  const card = ALL.find((c) => c.id === "to_target:Brotdose");
  assert.strictEqual(card.answer, "die Brotdose");
  assert.deepStrictEqual(plain(card.alternatives), ["die Brotbox"]);
  assert.strictEqual(card.options.article, true);
  assert.strictEqual(ALL.find((c) => c.id === "to_target:Eltern").answer, "die Eltern");
});

test("perfekt accepts both auxiliaries", () => {
  const card = ALL.find((c) => c.id === "perfekt:fahren");
  assert.strictEqual(card.answer, "hat gefahren");
  assert.deepStrictEqual(plain(card.alternatives), ["ist gefahren"]);
});

test("no card for an entry that is not ready", () => {
  assert.ok(!ALL.some((c) => c.entry === "unfertig"));
});

test("cloze takes the next sentence each time", () => {
  const card = ALL.find((c) => c.id === "cloze:Termin");
  const first = view(card, null);
  const second = view(card, { reps: 1, lapses: 0 });
  assert.strictEqual(first.prompt, "Der ___ ist morgen.");
  assert.strictEqual(first.answer, "Termin");
  assert.strictEqual(second.prompt, "Zwei ___, bitte.");
  assert.ok(second.alternatives.indexOf("Termin") >= 0);
});

test("separable card has two gaps", () => {
  const shown = view(ALL.find((c) => c.id === "separable:anrufen"), null);
  assert.strictEqual(shown.prompt, "Ich ___ dich ___.");
  assert.strictEqual(shown.answer, "rufe an");
});

test("roleplay, mistake and gap cards", () => {
  assert.deepStrictEqual(ids(ALL.filter((c) => c.exercise === "roleplay")).sort(), ["roleplay:other", "roleplay:talk"]);
  const mistake = ALL.find((c) => c.id === "mistake:m1");
  assert.strictEqual(mistake.kind, "mistake");
  assert.strictEqual(mistake.prompt, "Ich habe 40 Jahre.");
  assert.strictEqual(mistake.answer, "Ich bin 40 Jahre alt.");
  assert.deepStrictEqual(ids(ALL.filter((c) => c.exercise === "gap")), ["gap:g1"]);
  assert.strictEqual(ALL.find((c) => c.id === "gap:g1").check, "self");
});

test("daily puts due before new and respects limits", () => {
  const states = {
    "to_native:Termin": { due: "2026-11-05", interval: 3, ease: 2.5, reps: 2, lapses: 0, last: "2026-11-02", goods: 2 },
    "to_native:Brotdose": { due: "2026-11-10", interval: 3, ease: 2.5, reps: 2, lapses: 0, last: "2026-11-07", goods: 2 },
    "article:Termin": { due: "2026-11-01", interval: 3, ease: 2.5, reps: 2, lapses: 0, last: "2026-10-29", goods: 2 },
    "plural:Termin": { due: "2026-11-09", interval: 3, ease: 2.5, reps: 2, lapses: 0, last: "2026-11-06", goods: 2 },
    "to_native:neu": { due: "2026-12-01", interval: 30, ease: 2.5, reps: 4, lapses: 0, last: "2026-11-01", goods: 4 },
  };
  const list = session("daily", ALL, states, DATA, TODAY, {});
  assert.deepStrictEqual(ids(list.slice(0, 3)), ["article:Termin", "to_native:Termin", "plural:Termin"]);
  assert.strictEqual(list[3].exercise, "roleplay");
  const fresh = list.slice(4);
  assert.strictEqual(fresh.length, 2);
  assert.ok(fresh.every((c) => !states[c.id] && c.exercise !== "roleplay"));
});

test("daily picks the coming-up conversation", () => {
  const list = session("daily", ALL, {}, DATA, TODAY, {});
  assert.strictEqual(list.find((c) => c.exercise === "roleplay").id, "roleplay:talk");
});

test("new cards from coming-up situations first, then newest", () => {
  const list = session("daily", ALL, {}, DATA, TODAY, {}).filter((c) => c.exercise !== "roleplay");
  assert.strictEqual(list[0].entry, "Eltern");
  assert.strictEqual(list[1].entry, "Brotdose");
});

test("short has due cards only, at most 15", () => {
  const states = {};
  ALL.forEach((c) => { states[c.id] = { due: "2026-11-01", interval: 1, ease: 2.5, reps: 1, lapses: 0, last: "2026-10-31", goods: 1 }; });
  const list = session("short", ALL, states, DATA, TODAY, {});
  assert.strictEqual(list.length, Math.min(15, ALL.length));
});

test("weekly adds mistakes of the patterns with most lapses", () => {
  const states = { "mistake:m1": { due: "2026-12-01", interval: 3, ease: 2.1, reps: 1, lapses: 2, last: "2026-11-01", goods: 0 } };
  const list = session("weekly", ALL, states, DATA, TODAY, {});
  assert.ok(ids(list).indexOf("mistake:m1") >= 0);
  assert.ok(list.some((c) => c.exercise === "roleplay"));
});

test("free filters by situation, type and level", () => {
  const list = session("free", ALL, {}, DATA, TODAY, { situation: "Elternabend" });
  assert.deepStrictEqual([...new Set(list.map((c) => c.entry))].sort(), ["Eltern", "talk"]);
  const verbs = session("free", ALL, {}, DATA, TODAY, { type: "Verb" });
  assert.ok(verbs.length > 0 && verbs.every((c) => c.entry === "anrufen" || c.entry === "fahren"));
  assert.strictEqual(session("free", ALL, {}, DATA, TODAY, { level: "B2" }).length, 0);
});

test("counts of due and new", () => {
  const states = { "article:Termin": { due: "2026-11-01", interval: 3, ease: 2.5, reps: 2, lapses: 0, last: "2026-10-29", goods: 2 } };
  assert.deepStrictEqual(plain(counts(ALL, states, TODAY, DATA)), { due: 1, fresh: 2 });
});

test("empty data gives empty sessions", () => {
  const empty = { settings: SETTINGS, situations: [], entries: [], sentences: [] };
  assert.strictEqual(cards(empty).length, 0);
  for (const kind of ["daily", "short", "weekly", "free"]) {
    assert.strictEqual(session(kind, [], {}, empty, TODAY, {}).length, 0, kind);
  }
  assert.strictEqual(cards({}).length, 0);
});
