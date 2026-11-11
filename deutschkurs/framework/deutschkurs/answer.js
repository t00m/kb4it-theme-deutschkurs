// deutschkurs: typing rules for practice answers (spec 7.2). Pure functions, no DOM.
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});
  var RANK = { again: 0, hard: 1, good: 2 };

  // Composed letters (NFC); one kind of apostrophe and no quote marks; umlauts and ß as ae, oe, ue, ss;
  // one space between words; no final . ! ?
  function normalise(text) {
    return String(text || "").normalize("NFC")
      .replace(/[\u2018\u2019\u201A\u02BC`´]/g, "'")
      .replace(/["\u201C\u201D\u201E\u00AB\u00BB\u2039\u203A]/g, "")
      .replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue")
      .replace(/Ä/g, "Ae").replace(/Ö/g, "Oe").replace(/Ü/g, "Ue").replace(/ß/g, "ss")
      .replace(/\s+/g, " ").trim()
      .replace(/[.!?]+$/, "").trim();
  }

  function lowerFirst(text) {
    return text.charAt(0).toLowerCase() + text.slice(1);
  }

  function distance(a, b) {
    var prev = [], cur, i, j;
    for (j = 0; j <= b.length; j++) prev.push(j);
    for (i = 1; i <= a.length; i++) {
      cur = [i];
      for (j = 1; j <= b.length; j++) {
        cur.push(Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)));
      }
      prev = cur;
    }
    return prev[b.length];
  }

  // Letters to add (missing in the answer) and to delete (extra in the answer), as runs.
  function diff(given, expected) {
    var a = String(given || ""), b = String(expected || ""), i, j;
    var table = [];
    for (i = 0; i <= a.length; i++) {
      table.push([]);
      for (j = 0; j <= b.length; j++) table[i].push(0);
    }
    for (i = a.length - 1; i >= 0; i--) {
      for (j = b.length - 1; j >= 0; j--) {
        table[i][j] = a[i] === b[j] ? table[i + 1][j + 1] + 1 : Math.max(table[i + 1][j], table[i][j + 1]);
      }
    }
    var ops = [];
    function push(op, ch) {
      var last = ops[ops.length - 1];
      if (last && last.op === op) last.text += ch;
      else ops.push({ op: op, text: ch });
    }
    i = 0; j = 0;
    while (i < a.length && j < b.length) {
      if (a[i] === b[j]) { push("same", a[i]); i++; j++; }
      else if (table[i + 1][j] >= table[i][j + 1]) { push("del", a[i]); i++; }
      else { push("add", b[j]); j++; }
    }
    while (i < a.length) { push("del", a[i]); i++; }
    while (j < b.length) { push("add", b[j]); j++; }
    return ops;
  }

  function firstWord(text) {
    return text.split(" ")[0].toLowerCase();
  }

  // Rate one answer against one expected text.
  function rateOne(given, expected, options) {
    var g = normalise(given), e = normalise(expected);
    if (!g) return "again";
    if (options.article && firstWord(g) !== firstWord(e)) return "again";
    // A leading capital is ignored, except on a noun typed without its article.
    var foldFirst = !options.noun || options.article;
    if (foldFirst) { g = lowerFirst(g); e = lowerFirst(e); }
    if (g === e) return "good";
    var gl = g.toLowerCase(), el = e.toLowerCase();
    if (gl === el) return "hard";
    var allowed = el.length > 8 ? 2 : 1;
    return distance(gl, el) <= allowed ? "hard" : "again";
  }

  // {result, diff}: the best rating against the expected text and its alternatives.
  function check(given, expected, options) {
    var opts = options || {};
    var candidates = [expected].concat(opts.alternatives || []);
    var best = "again", target = expected, k, found;
    for (k = 0; k < candidates.length; k++) {
      found = rateOne(given, candidates[k], opts);
      if (RANK[found] > RANK[best]) { best = found; target = candidates[k]; }
    }
    return { result: best, expected: target,
             diff: best === "good" ? [] : diff(normalise(given), normalise(target)) };
  }

  dk.answer = { normalise: normalise, check: check, diff: diff, distance: distance };
})(typeof window !== "undefined" ? window : this);
