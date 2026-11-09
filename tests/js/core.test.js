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
