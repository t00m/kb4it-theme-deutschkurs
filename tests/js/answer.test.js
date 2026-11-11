const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const SOURCE = fs.readFileSync(
  path.join(__dirname, "..", "..", "deutschkurs", "framework", "deutschkurs", "answer.js"), "utf8");
const context = {};
vm.runInNewContext(SOURCE, context);
const { normalise, check, diff } = context.Deutschkurs.answer;

test("normalises umlaut spellings", () => {
  assert.strictEqual(normalise("Maedchen"), normalise("Mädchen"));
  assert.strictEqual(normalise("Strasse"), normalise("Straße"));
  assert.strictEqual(check("muede", "müde").result, "good");
  assert.strictEqual(check("Grüsse", "Grüße").result, "good");
});

test("ignores case of first letter, spaces and final punctuation", () => {
  assert.strictEqual(check("ich bin müde", "Ich bin müde.").result, "good");
  assert.strictEqual(check("  Ich   bin müde!  ", "Ich bin müde").result, "good");
  assert.strictEqual(check("Bis morgen?", "bis morgen").result, "good");
});

test("wrong article is again", () => {
  assert.strictEqual(check("die Termin", "der Termin", { article: true, noun: true }).result, "again");
  assert.strictEqual(check("der Termin", "der Termin", { article: true, noun: true }).result, "good");
});

test("lowercase noun is hard", () => {
  assert.strictEqual(check("der termin", "der Termin", { article: true, noun: true }).result, "hard");
  assert.strictEqual(check("termine", "Termine", { noun: true }).result, "hard");
});

test("one typo in a short word is hard", () => {
  assert.strictEqual(check("Termn", "Termin").result, "hard");
  assert.strictEqual(check("Trmn", "Termin").result, "again");
});

test("two typos in a long word are hard", () => {
  assert.strictEqual(check("Elternabnd", "Elternabend").result, "hard");
  assert.strictEqual(check("Eltrnabnd", "Elternabend").result, "hard");
  assert.strictEqual(check("Eltrnbnd", "Elternabend").result, "again");
});

test("an alternative counts as the answer", () => {
  assert.strictEqual(check("die Brotbox", "die Brotdose", { article: true, noun: true,
    alternatives: ["die Brotbox"] }).result, "good");
});

test("diff marks inserted and removed letters", () => {
  const ops = diff("Termn", "Termin");
  assert.deepStrictEqual(JSON.parse(JSON.stringify(ops)),
    [{ op: "same", text: "Term" }, { op: "add", text: "i" }, { op: "same", text: "n" }]);
  const extra = diff("Terrmin", "Termin");
  assert.deepStrictEqual(JSON.parse(JSON.stringify(extra)),
    [{ op: "same", text: "Ter" }, { op: "del", text: "r" }, { op: "same", text: "min" }]);
});

test("a wrong answer comes with its diff", () => {
  const found = check("Termn", "Termin");
  assert.ok(found.diff.length > 0);
});

test("empty answer is again", () => {
  assert.strictEqual(check("", "Termin").result, "again");
  assert.strictEqual(check("   ", "Termin").result, "again");
});
