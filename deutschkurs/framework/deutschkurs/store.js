// deutschkurs: learner progress in localStorage, with export and import (spec 7.5). No DOM.
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});
  var FORMAT = "deutschkurs-progress";

  function parse(text, fallback) {
    try {
      var value = JSON.parse(text);
      return value === null || value === undefined ? fallback : value;
    } catch (e) {
      return fallback;
    }
  }

  function isObject(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  var DAY = /^\d{4}-\d{2}-\d{2}$/;

  function count(value) {
    return typeof value === "number" && value >= 0 && Math.floor(value) === value;
  }

  // A card state as the scheduler writes it; anything else would keep a card from ever coming due.
  function validState(state) {
    if (!isObject(state)) return false;
    if (typeof state.due !== "string" || !DAY.test(state.due)) return false;
    if (typeof state.interval !== "number" || !isFinite(state.interval) || state.interval < 0) return false;
    if (typeof state.ease !== "number" || !isFinite(state.ease) || state.ease <= 0) return false;
    if (!count(state.reps) || !count(state.lapses)) return false;
    if (state.goods !== undefined && !count(state.goods)) return false;
    if (state.last !== undefined && state.last !== "" && (typeof state.last !== "string" || !DAY.test(state.last))) return false;
    if (state.first !== undefined && state.first !== "" && (typeof state.first !== "string" || !DAY.test(state.first))) return false;
    return true;
  }

  function validCards(found) {
    var cards = {};
    for (var key in found) if (validState(found[key])) cards[key] = found[key];
    return cards;
  }

  // Other courses with saved cards in this storage, most cards first: progress kept under an old course title.
  function others(storage, site) {
    var found = [];
    if (!storage) return found;
    try {
      for (var i = 0; i < storage.length; i++) {
        var match = /^deutschkurs\.(.+)\.cards$/.exec(storage.key(i) || "");
        if (!match || match[1] === site) continue;
        var cards = parse(storage.getItem(match[0]), {});
        var n = isObject(cards) ? Object.keys(validCards(cards)).length : 0;
        if (n) found.push({ site: match[1], cards: n });
      }
    } catch (e) {
      return [];
    }
    return found.sort(function (a, b) { return b.cards - a.cards || (a.site < b.site ? -1 : 1); });
  }

  // A store for one course. Storage that throws or is missing gives a store in memory with ok false.
  function open(storage, site) {
    var prefix = "deutschkurs." + site + ".";
    var ok = !!storage;
    var cards = {}, days = [];
    if (ok) {
      try {
        storage.setItem(prefix + "probe", "1");
        storage.removeItem(prefix + "probe");
        var storedCards = parse(storage.getItem(prefix + "cards"), {});
        var storedDays = parse(storage.getItem(prefix + "days"), []);
        cards = isObject(storedCards) ? validCards(storedCards) : {};
        days = Array.isArray(storedDays) ? storedDays : [];
      } catch (e) {
        ok = false;
      }
    }

    function write() {
      if (!ok) return;
      try {
        storage.setItem(prefix + "cards", JSON.stringify(cards));
        storage.setItem(prefix + "days", JSON.stringify(days));
      } catch (e) {
        ok = false;
        store.ok = false;
      }
    }

    var store = {
      ok: ok,
      cards: function () { return cards; },
      days: function () { return days; },
      // False when the browser did not keep it (storage full or blocked); the card stays in memory.
      save: function (id, state) { cards[id] = state; write(); return store.ok; },
      studied: function (day) {
        if (days.indexOf(day) < 0) { days.push(day); days.sort(); }
        write();
      },
      replace: function (newCards, newDays) { cards = newCards; days = newDays; write(); },
    };
    return store;
  }

  function exportJson(store, site, today) {
    return JSON.stringify({ format: FORMAT, version: 1, site: site, exported: today, cards: store.cards(),
                            days: store.days() }, null, 1);
  }

  // Merge a progress file: per card the later "last" wins; cards this course does not have are skipped.
  function merge(local, text, known) {
    var cards = {}, days = (local.days || []).slice(), key;
    for (key in local.cards || {}) cards[key] = local.cards[key];
    var file = parse(text, null);
    if (!isObject(file) || file.format !== FORMAT || !isObject(file.cards)) {
      return { cards: cards, days: days, merged: 0, skipped: 0, error: "invalid" };
    }
    var merged = 0, skipped = 0;
    for (key in file.cards) {
      var state = file.cards[key];
      if ((known || []).indexOf(key) < 0 || !validState(state)) { skipped += 1; continue; }
      if (!cards[key] || String(state.last || "") > String(cards[key].last || "")) {
        cards[key] = state;
        merged += 1;
      }
    }
    (Array.isArray(file.days) ? file.days : []).forEach(function (day) {
      if (typeof day === "string" && days.indexOf(day) < 0) days.push(day);
    });
    days.sort();
    return { cards: cards, days: days, merged: merged, skipped: skipped, error: "" };
  }

  dk.store = { open: open, exportJson: exportJson, merge: merge, validState: validState, others: others, FORMAT: FORMAT };
})(typeof window !== "undefined" ? window : this);
