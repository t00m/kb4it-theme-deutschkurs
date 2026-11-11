const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const SOURCE = fs.readFileSync(
  path.join(__dirname, "..", "..", "deutschkurs", "framework", "deutschkurs", "scheduler.js"), "utf8");
const context = {};
vm.runInNewContext(SOURCE, context);
const { fresh, rate, isDue, addDays } = context.Deutschkurs.scheduler;
const DAY = "2026-11-11";

test("a fresh card", () => {
  assert.deepStrictEqual(JSON.parse(JSON.stringify(fresh())),
    { due: "", interval: 0, ease: 2.5, reps: 0, lapses: 0, last: "", goods: 0 });
});

test("good gives 1 then 3 then interval times ease", () => {
  let s = rate(fresh(), "good", DAY);
  assert.strictEqual(s.interval, 1);
  assert.strictEqual(s.due, "2026-11-12");
  assert.strictEqual(s.last, DAY);
  s = rate(s, "good", "2026-11-12");
  assert.strictEqual(s.interval, 3);
  s = rate(s, "good", "2026-11-15");
  assert.strictEqual(s.interval, 8);
  assert.strictEqual(s.due, "2026-11-23");
});

test("rate returns a new object", () => {
  const before = fresh();
  rate(before, "good", DAY);
  assert.strictEqual(before.interval, 0);
});

test("again resets to one day and lowers ease to at least 1.3", () => {
  let s = { due: DAY, interval: 20, ease: 1.4, reps: 5, lapses: 0, last: "", goods: 4 };
  s = rate(s, "again", DAY);
  assert.strictEqual(s.interval, 1);
  assert.strictEqual(s.lapses, 1);
  assert.strictEqual(s.ease, 1.3);
  assert.strictEqual(s.reps, 0);
  s = rate(s, "good", "2026-11-12");
  assert.strictEqual(s.interval, 1);
});

test("hard multiplies by 1.2 and lowers ease", () => {
  const s = rate({ due: DAY, interval: 10, ease: 2.5, reps: 3, lapses: 0, last: "", goods: 3 }, "hard", DAY);
  assert.strictEqual(s.interval, 12);
  assert.strictEqual(s.ease, 2.35);
  const first = rate(fresh(), "hard", DAY);
  assert.strictEqual(first.interval, 1);
});

test("mistake stays at one day until three goods in a row", () => {
  let s = fresh();
  s = rate(s, "good", DAY, "mistake");
  assert.strictEqual(s.interval, 1);
  s = rate(s, "good", "2026-11-12", "mistake");
  assert.strictEqual(s.interval, 1);
  s = rate(s, "good", "2026-11-13", "mistake");
  assert.strictEqual(s.goods, 3);
  assert.ok(s.interval > 1);
});

test("again on a mistake resets the goods counter", () => {
  let s = rate(rate(fresh(), "good", DAY, "mistake"), "good", "2026-11-12", "mistake");
  s = rate(s, "again", "2026-11-13", "mistake");
  assert.strictEqual(s.goods, 0);
  s = rate(s, "good", "2026-11-14", "mistake");
  assert.strictEqual(s.interval, 1);
});

test("due on the due day and after", () => {
  const s = rate(fresh(), "good", DAY);
  assert.ok(!isDue(s, DAY));
  assert.ok(isDue(s, "2026-11-12"));
  assert.ok(isDue(s, "2026-12-01"));
  assert.ok(isDue(fresh(), DAY));
});

test("addDays crosses month and year", () => {
  assert.strictEqual(addDays("2026-11-30", 1), "2026-12-01");
  assert.strictEqual(addDays("2026-12-31", 1), "2027-01-01");
  assert.strictEqual(addDays("2028-02-28", 1), "2028-02-29");
});
