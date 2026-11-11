const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const SOURCE = fs.readFileSync(
  path.join(__dirname, "..", "..", "deutschkurs", "framework", "deutschkurs", "core.js"), "utf8");
const context = {};
vm.runInNewContext(SOURCE, context);
const { rowMatches } = context.Deutschkurs;
const ROW = ["der", "Termin", "die Termine", "cita", "A1", "noun"];

test("empty filters match every row", () => {
  assert.ok(rowMatches(ROW, "", {}));
});

test("text matches any cell, case-insensitive", () => {
  assert.ok(rowMatches(ROW, "CITA", {}));
  assert.ok(!rowMatches(ROW, "Kind", {}));
});

test("column filters need an exact cell", () => {
  assert.ok(rowMatches(ROW, "", { 4: "A1" }));
  assert.ok(!rowMatches(ROW, "", { 4: "A2" }));
  assert.ok(rowMatches(ROW, "", { 4: "" }));
});

const { dateState, initDates, initDialogues } = context.Deutschkurs;
const TODAY = "2026-11-09";

// A small stand-in for a DOM element.
function element(attrs) {
  const classes = new Set();
  const listeners = {};
  return {
    hidden: Boolean(attrs && attrs.hidden),
    textContent: "",
    getAttribute: (name) => (attrs && name in attrs ? attrs[name] : null),
    classList: {
      add: (name) => classes.add(name),
      remove: (name) => classes.delete(name),
      contains: (name) => classes.has(name),
    },
    addEventListener: (type, fn) => { listeners[type] = fn; },
    click: () => listeners.click({}),
  };
}

test("a day before today is past, today is soon", () => {
  assert.strictEqual(dateState("2026-11-08", TODAY), "past");
  assert.strictEqual(dateState("2026-11-09", TODAY), "soon");
});

test("without a number of days every future day is soon", () => {
  assert.strictEqual(dateState("2027-03-01", TODAY), "soon");
});

test("with a number of days a far day is later", () => {
  assert.strictEqual(dateState("2026-11-16", TODAY, 7), "soon");
  assert.strictEqual(dateState("2026-11-17", TODAY, 7), "later");
  assert.strictEqual(dateState("2026-11-08", TODAY, 7), "past");
});

test("a date with a time counts by its day", () => {
  assert.strictEqual(dateState("2026-11-09 08:00", TODAY), "soon");
});

test("impossible or unreadable dates are invalid", () => {
  assert.strictEqual(dateState("2026-02-30", TODAY), "invalid");
  assert.strictEqual(dateState("20.11.2026", TODAY), "invalid");
  assert.strictEqual(dateState("", TODAY), "invalid");
  assert.strictEqual(dateState(null, TODAY), "invalid");
  assert.strictEqual(dateState("2026-11-10", "heute"), "invalid");
});

test("dated blocks are hidden in the states they name", () => {
  const past = element({ "data-date": "2026-11-01", "data-hide": "past" });
  const open = element({ "data-date": "2026-11-20", "data-hide": "past" });
  const far = element({ "data-date": "2026-12-24", "data-days": "7", "data-hide": "past later" });
  const near = element({ "data-date": "2026-11-12", "data-days": "7", "data-hide": "past later" });
  const broken = element({ "data-date": "bald", "data-hide": "past later" });
  const all = [past, open, far, near, broken];
  initDates({ querySelectorAll: (selector) => (selector === "[data-date]" ? all : []) }, TODAY);
  assert.deepStrictEqual([past.hidden, open.hidden, far.hidden, near.hidden, broken.hidden],
    [true, false, true, false, false]);
  assert.ok(open.classList.contains("dk-date-soon"));
  assert.ok(far.classList.contains("dk-date-later"));
});

test("the script hides the translations of turns and shows the button", () => {
  const root = element();
  const button = element({ hidden: true, "data-show": "Show translations", "data-hide": "Hide translations" });
  initDialogues({ documentElement: root, querySelectorAll: () => [button] });
  assert.ok(root.classList.contains("dk-hide-tr"));
  assert.strictEqual(button.hidden, false);
  assert.strictEqual(button.textContent, "Show translations");
  button.click();
  assert.ok(!root.classList.contains("dk-hide-tr"));
  assert.strictEqual(button.textContent, "Hide translations");
  button.click();
  assert.ok(root.classList.contains("dk-hide-tr"));
  assert.strictEqual(button.textContent, "Show translations");
});

test("a page without a dialogue keeps its translations", () => {
  const root = element();
  initDialogues({ documentElement: root, querySelectorAll: () => [] });
  assert.ok(!root.classList.contains("dk-hide-tr"));
});

test("a dated block is hidden when all its dated items are", () => {
  const gone = element({ "data-date": "2026-11-01", "data-hide": "past" });
  const open = element({ "data-date": "2026-11-20", "data-hide": "past" });
  const empty = element();
  const used = element();
  const doc = {
    querySelectorAll: (selector) => (selector === ".dk-dated" ? [empty, used] : [gone, open]),
  };
  empty.querySelectorAll = () => [gone];
  used.querySelectorAll = () => [gone, open];
  initDates(doc, TODAY);
  assert.deepStrictEqual([empty.hidden, used.hidden], [true, false]);
});

test("galleryMatch filters by place and situation", () => {
  const { galleryMatch } = context.Deutschkurs;
  const item = { place: "Street", situations: ["Unterwegs", "Am Schultor"] };
  assert.strictEqual(galleryMatch(item, "", ""), true);
  assert.strictEqual(galleryMatch(item, "Street", ""), true);
  assert.strictEqual(galleryMatch(item, "Shop", ""), false);
  assert.strictEqual(galleryMatch(item, "", "Am Schultor"), true);
  assert.strictEqual(galleryMatch(item, "Street", "Elternabend"), false);
});

test("a column filter matches one of several values in a cell", () => {
  const row = ["Kind", "die Kinder", "child", "A1", "Familie, Schule"];
  assert.ok(rowMatches(row, "", { 4: "Schule" }));
  assert.ok(rowMatches(row, "", { 4: "Familie" }));
  assert.ok(!rowMatches(row, "", { 4: "Arbeit" }));
  assert.ok(!rowMatches(row, "", { 4: "Fam" }));
});
