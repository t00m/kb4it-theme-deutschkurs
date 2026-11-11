const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const DIR = path.join(__dirname, "..", "..", "deutschkurs", "framework", "deutschkurs");
const context = {};
for (const name of ["scheduler.js", "progress.js"]) {
  vm.runInNewContext(fs.readFileSync(path.join(DIR, name), "utf8"), context);
}
const { known, patterns, calendar } = context.Deutschkurs.progress;
const plain = (x) => JSON.parse(JSON.stringify(x));

const DATA = { entries: [
  { id: "a", type: "Word", level: "A1" }, { id: "b", type: "Word", level: "A1" }, { id: "c", type: "Verb", level: "A2" },
  { id: "g", type: "Grammar", level: "A1" },
  { id: "m1", type: "Mistake", level: "A1", pattern: "es-tener" }, { id: "m2", type: "Mistake", level: "A1", pattern: "es-tener" },
  { id: "m3", type: "Mistake", level: "A2", pattern: "" },
] };
const st = (interval, lapses) => ({ due: "2026-12-01", interval, ease: 2.5, reps: 3, lapses: lapses || 0,
                                     last: "2026-11-10", goods: 3 });

test("known counts passive and active per level", () => {
  const states = { "to_native:a": st(7), "to_native:b": st(6), "to_target:a": st(10), "to_native:c": st(30) };
  assert.deepStrictEqual(plain(known(states, DATA)), {
    A1: { passive: 1, active: 1, total: 2 },
    A2: { passive: 1, active: 0, total: 1 },
  });
});

test("patterns sum entries and lapses, most lapses first", () => {
  const states = { "mistake:m1": st(1, 2), "mistake:m2": st(1, 1), "mistake:m3": st(1, 5) };
  assert.deepStrictEqual(plain(patterns(states, DATA)), [
    { pattern: "", entries: 1, lapses: 5 },
    { pattern: "es-tener", entries: 2, lapses: 3 },
  ]);
});

test("calendar marks study days in whole weeks ending with today", () => {
  const weeks = calendar(["2026-11-09", "2026-11-11", "2026-10-01"], "2026-11-11", 2);
  assert.strictEqual(weeks.length, 2);
  const days = weeks.flat();
  assert.strictEqual(days.length, 14);
  assert.strictEqual(days[0].day, "2026-11-02");
  assert.ok(days.find((d) => d.day === "2026-11-09").studied);
  assert.ok(days.find((d) => d.day === "2026-11-11").studied);
  assert.ok(!days.find((d) => d.day === "2026-11-10").studied);
  assert.ok(days.find((d) => d.day === "2026-11-12").future);
  assert.ok(!days.find((d) => d.day === "2026-11-11").future);
});

test("empty progress", () => {
  assert.deepStrictEqual(plain(known({}, { entries: [] })), {});
  assert.deepStrictEqual(plain(patterns({}, { entries: [] })), []);
  assert.strictEqual(calendar([], "2026-11-11", 1).flat().filter((d) => d.studied).length, 0);
});
