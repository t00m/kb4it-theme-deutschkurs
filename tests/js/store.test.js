const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const SOURCE = fs.readFileSync(
  path.join(__dirname, "..", "..", "deutschkurs", "framework", "deutschkurs", "store.js"), "utf8");
const context = {};
vm.runInNewContext(SOURCE, context);
const { open, exportJson, merge } = context.Deutschkurs.store;
const plain = (x) => JSON.parse(JSON.stringify(x));

function memoryStorage() {
  const data = {};
  return {
    data,
    getItem: (k) => (k in data ? data[k] : null),
    setItem: (k, v) => { data[k] = String(v); },
    removeItem: (k) => { delete data[k]; },
  };
}
const throwing = {
  getItem: () => { throw new Error("blocked"); },
  setItem: () => { throw new Error("blocked"); },
  removeItem: () => { throw new Error("blocked"); },
};
const STATE = { due: "2026-11-12", interval: 1, ease: 2.5, reps: 1, lapses: 0, last: "2026-11-11", goods: 1 };

test("save and reload a card", () => {
  const storage = memoryStorage();
  const store = open(storage, "abc");
  assert.strictEqual(store.ok, true);
  store.save("article:termin.md", STATE);
  store.studied("2026-11-11");
  store.studied("2026-11-11");
  const again = open(storage, "abc");
  assert.deepStrictEqual(plain(again.cards()), { "article:termin.md": STATE });
  assert.deepStrictEqual(plain(again.days()), ["2026-11-11"]);
  assert.ok("deutschkurs.abc.cards" in storage.data && "deutschkurs.abc.days" in storage.data);
});

test("courses do not share progress", () => {
  const storage = memoryStorage();
  open(storage, "abc").save("article:termin.md", STATE);
  assert.deepStrictEqual(plain(open(storage, "xyz").cards()), {});
});

test("throwing storage falls back to memory", () => {
  const store = open(throwing, "abc");
  assert.strictEqual(store.ok, false);
  store.save("article:termin.md", STATE);
  assert.deepStrictEqual(plain(store.cards()), { "article:termin.md": STATE });
  assert.strictEqual(open(null, "abc").ok, false);
});

test("broken stored json starts empty", () => {
  const storage = memoryStorage();
  storage.setItem("deutschkurs.abc.cards", "{not json");
  assert.deepStrictEqual(plain(open(storage, "abc").cards()), {});
});

test("export has format version site cards days", () => {
  const store = open(memoryStorage(), "abc");
  store.save("article:termin.md", STATE);
  store.studied("2026-11-11");
  const file = JSON.parse(exportJson(store, "abc", "2026-11-11"));
  assert.deepStrictEqual(file, { format: "deutschkurs-progress", version: 1, site: "abc", exported: "2026-11-11",
                                 cards: { "article:termin.md": STATE }, days: ["2026-11-11"] });
});

test("merge keeps the later last", () => {
  const local = { cards: { a: Object.assign({}, STATE, { last: "2026-11-10", interval: 3 }),
                           b: Object.assign({}, STATE, { last: "2026-11-11", interval: 5 }) },
                  days: ["2026-11-10"] };
  const incoming = JSON.stringify({ format: "deutschkurs-progress", version: 1, site: "other",
    cards: { a: Object.assign({}, STATE, { last: "2026-11-11", interval: 7 }),
             b: Object.assign({}, STATE, { last: "2026-11-01", interval: 1 }) },
    days: ["2026-11-11", "2026-11-01"] });
  const result = merge(local, incoming, ["a", "b"]);
  assert.strictEqual(result.error, "");
  assert.strictEqual(result.cards.a.interval, 7);
  assert.strictEqual(result.cards.b.interval, 5);
  assert.strictEqual(result.merged, 1);
  assert.deepStrictEqual(plain(result.days), ["2026-11-01", "2026-11-10", "2026-11-11"]);
});

test("merge skips cards of unknown entries", () => {
  const incoming = JSON.stringify({ format: "deutschkurs-progress", version: 1, site: "abc",
    cards: { gone: STATE, a: STATE }, days: [] });
  const result = merge({ cards: {}, days: [] }, incoming, ["a"]);
  assert.strictEqual(result.merged, 1);
  assert.strictEqual(result.skipped, 1);
  assert.ok(!("gone" in result.cards));
});

test("merge of broken json changes nothing", () => {
  const local = { cards: { a: STATE }, days: ["2026-11-11"] };
  for (const bad of ["{oops", "[]", JSON.stringify({ format: "other", cards: {} }), "null", ""]) {
    const result = merge(local, bad, ["a"]);
    assert.notStrictEqual(result.error, "", bad);
    assert.deepStrictEqual(plain(result.cards), plain(local.cards), bad);
    assert.deepStrictEqual(plain(result.days), plain(local.days), bad);
    assert.strictEqual(result.merged, 0);
  }
});

test("store replaces its cards and days after an import", () => {
  const storage = memoryStorage();
  const store = open(storage, "abc");
  store.replace({ a: STATE }, ["2026-11-01"]);
  assert.deepStrictEqual(plain(open(storage, "abc").cards()), { a: STATE });
  assert.deepStrictEqual(plain(open(storage, "abc").days()), ["2026-11-01"]);
});
