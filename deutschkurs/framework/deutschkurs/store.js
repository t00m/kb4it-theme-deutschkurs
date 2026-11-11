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
        cards = isObject(storedCards) ? storedCards : {};
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
      save: function (id, state) { cards[id] = state; write(); },
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
      if ((known || []).indexOf(key) < 0 || !isObject(state)) { skipped += 1; continue; }
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

  dk.store = { open: open, exportJson: exportJson, merge: merge, FORMAT: FORMAT };
})(typeof window !== "undefined" ? window : this);
