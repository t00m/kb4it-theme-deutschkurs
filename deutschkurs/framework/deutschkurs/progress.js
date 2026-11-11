// deutschkurs: the parts of the Progress page that depend on the learner's answers (spec 7.6).
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});
  var VOCABULARY = ["Word", "Verb", "Chunk"];
  // An interval of 7 days or more counts as known.
  var KNOWN = 7;

  function interval(states, id) {
    return (states[id] && states[id].interval) || 0;
  }

  // Per level: entries understood (to_native), entries said (to_target) and all entries.
  function known(states, data) {
    var found = {};
    ((data && data.entries) || []).forEach(function (e) {
      if (VOCABULARY.indexOf(e.type) < 0 || !e.level) return;
      var row = found[e.level] = found[e.level] || { passive: 0, active: 0, total: 0 };
      row.total += 1;
      if (interval(states, "to_native:" + e.id) >= KNOWN) row.passive += 1;
      if (interval(states, "to_target:" + e.id) >= KNOWN) row.active += 1;
    });
    return found;
  }

  // Mistake patterns with their number of entries and lapses, most lapses first.
  function patterns(states, data) {
    var found = {}, order = [];
    ((data && data.entries) || []).forEach(function (e) {
      if (e.type !== "Mistake") return;
      var key = e.pattern || "";
      if (!found[key]) { found[key] = { pattern: key, entries: 0, lapses: 0 }; order.push(key); }
      found[key].entries += 1;
      found[key].lapses += (states["mistake:" + e.id] && states["mistake:" + e.id].lapses) || 0;
    });
    return order.map(function (k) { return found[k]; }).sort(function (a, b) { return b.lapses - a.lapses; });
  }

  function weekday(day) {
    var p = day.split("-");
    return (new Date(Date.UTC(Number(p[0]), Number(p[1]) - 1, Number(p[2]))).getUTCDay() + 6) % 7;
  }

  // Whole weeks, Monday first, the last one holding today; each day says if it was studied.
  function calendar(days, today, weeks) {
    var add = dk.scheduler.addDays;
    var start = add(add(today, -weekday(today)), -7 * (weeks - 1));
    var out = [];
    for (var w = 0; w < weeks; w++) {
      var week = [];
      for (var d = 0; d < 7; d++) {
        var day = add(start, w * 7 + d);
        week.push({ day: day, studied: (days || []).indexOf(day) >= 0, future: day > today });
      }
      out.push(week);
    }
    return out;
  }

  function el(tag, attrs, children) {
    var node = root.document.createElement(tag);
    for (var key in attrs || {}) {
      if (key === "text") node.textContent = attrs[key];
      else if (key === "className") node.className = attrs[key];
      else node.setAttribute(key, attrs[key]);
    }
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  function init(doc) {
    var knownBox = doc.getElementById("dk-known");
    var data = root.DEUTSCHKURS_DATA;
    if (!knownBox || !data || !dk.store) return;
    var L = {};
    try { L = JSON.parse(doc.getElementById("dk-practice-labels").textContent); } catch (e) { L = {}; }
    var store = dk.store.open((function () { try { return root.localStorage; } catch (e) { return null; } })(), data.site);
    var states = store.cards();
    var now = new Date();
    var today = dk.scheduler.addDays(now.getFullYear() + "-" + (now.getMonth() + 1) + "-" + now.getDate(), 0);

    var levels = known(states, data);
    var rows = Object.keys(levels).sort().map(function (level) {
      var r = levels[level];
      return el("tr", {}, [el("td", { text: level }), el("td", { text: r.passive + " / " + r.total }),
                           el("td", { text: r.active + " / " + r.total })]);
    });
    knownBox.textContent = "";
    knownBox.appendChild(el("table", { className: "uk-table uk-table-small uk-table-divider" }, [
      el("thead", {}, [el("tr", {}, [el("th", { text: L.level }), el("th", { text: L.passive }),
                                     el("th", { text: L.active })])]),
      el("tbody", {}, rows)]));

    var patternBox = doc.getElementById("dk-patterns");
    patternBox.textContent = "";
    patternBox.appendChild(el("ul", { className: "uk-list uk-list-divider" }, patterns(states, data).map(function (p) {
      return el("li", {}, [el("span", { text: p.pattern || L.no_pattern }),
                           el("span", { className: "dk-note", text: " " + p.entries + " · " + L.lapses + ": " + p.lapses })]);
    })));

    var calendarBox = doc.getElementById("dk-calendar");
    calendarBox.textContent = "";
    calendarBox.appendChild(el("div", { className: "dk-calendar-grid" }, calendar(store.days(), today, 12).map(function (week) {
      return el("div", { className: "dk-week" }, week.map(function (d) {
        return el("span", { className: "dk-day" + (d.studied ? " dk-studied" : "") + (d.future ? " dk-future" : ""),
                            title: d.day });
      }));
    })));
  }

  dk.progress = { known: known, patterns: patterns, calendar: calendar, init: init };

  if (root.document && root.document.addEventListener) {
    root.document.addEventListener("DOMContentLoaded", function () { init(root.document); });
  }
})(typeof window !== "undefined" ? window : this);
