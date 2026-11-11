// deutschkurs: shared namespace, the filter of list tables, dated blocks and dialogues.
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});

  // True when a row's cells match the text and every column filter.
  function rowMatches(cells, text, columns) {
    var needle = (text || "").trim().toLowerCase();
    if (needle && cells.join(" ").toLowerCase().indexOf(needle) < 0) return false;
    for (var key in columns) {
      // A cell may hold several values joined by ", " (a noun with two topics); one of them must match.
      if (columns[key] && cells[key] !== columns[key] &&
          String(cells[key]).split(",").map(function (v) { return v.trim(); }).indexOf(columns[key]) < 0) return false;
    }
    return true;
  }

  function initFilters(doc) {
    var tables = {};
    var controls = doc.querySelectorAll(".dk-filter, .dk-filter-select");
    Array.prototype.forEach.call(controls, function (control) {
      var id = control.getAttribute("data-table");
      (tables[id] = tables[id] || []).push(control);
      control.addEventListener("input", function () { apply(id); });
    });

    function apply(id) {
      var table = doc.getElementById(id);
      if (!table) return;
      var text = "";
      var columns = {};
      tables[id].forEach(function (control) {
        if (control.classList.contains("dk-filter")) text = control.value;
        else columns[control.getAttribute("data-column")] = control.value;
      });
      Array.prototype.forEach.call(table.querySelectorAll("tr.dk-row"), function (row) {
        var cells = Array.prototype.map.call(row.cells, function (c) { return c.textContent.trim(); });
        row.hidden = !rowMatches(cells, text, columns);
      });
    }
  }

  // Day number of "YYYY-MM-DD", with or without a time; null when it is no real date.
  function dayNumber(text) {
    var match = /^(\d{4})-(\d{2})-(\d{2})(?:[ T]\d{2}:\d{2}(?::\d{2})?)?$/.exec(String(text || ""));
    if (!match) return null;
    var year = Number(match[1]), month = Number(match[2]), day = Number(match[3]);
    var date = new Date(Date.UTC(year, month - 1, day));
    if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
    return date.getTime() / 86400000;
  }

  // "past" before today; "later" when more than `days` days away; "soon" otherwise; "invalid" for a bad date.
  function dateState(date, today, days) {
    var then = dayNumber(date), now = dayNumber(today);
    if (then === null || now === null) return "invalid";
    if (then < now) return "past";
    if (days !== undefined && days !== null && then - now > Number(days)) return "later";
    return "soon";
  }

  function localDay(now) {
    function two(n) { return (n < 10 ? "0" : "") + n; }
    return now.getFullYear() + "-" + two(now.getMonth() + 1) + "-" + two(now.getDate());
  }

  // Dated blocks are always in the page; hide the ones whose state is listed in data-hide.
  function initDates(doc, today) {
    var day = today || localDay(new Date());
    Array.prototype.forEach.call(doc.querySelectorAll("[data-date]"), function (block) {
      var days = block.getAttribute("data-days");
      var state = dateState(block.getAttribute("data-date"), day, days === null || days === "" ? null : days);
      var hide = (block.getAttribute("data-hide") || "").split(" ");
      block.classList.add("dk-date-" + state);
      if (state !== "invalid" && hide.indexOf(state) >= 0) block.hidden = true;
    });
    // A block with a heading goes away when none of its dated items is left.
    Array.prototype.forEach.call(doc.querySelectorAll(".dk-dated"), function (group) {
      var items = group.querySelectorAll("[data-date]");
      var open = Array.prototype.some.call(items, function (item) { return !item.hidden; });
      if (items.length && !open) group.hidden = true;
    });
  }

  // Translations of turns show without this script; with it they hide behind a button.
  function initDialogues(doc) {
    var buttons = doc.querySelectorAll(".dk-toggle-tr");
    if (!buttons.length) return;
    var page = doc.documentElement;

    function label() {
      var hidden = page.classList.contains("dk-hide-tr");
      Array.prototype.forEach.call(buttons, function (button) {
        button.textContent = button.getAttribute(hidden ? "data-show" : "data-hide");
      });
    }

    page.classList.add("dk-hide-tr");
    Array.prototype.forEach.call(buttons, function (button) {
      button.hidden = false;
      button.addEventListener("click", function () {
        if (page.classList.contains("dk-hide-tr")) page.classList.remove("dk-hide-tr");
        else page.classList.add("dk-hide-tr");
        label();
      });
    });
    label();
  }

  // True when a photo has the chosen place and situation; an empty choice matches every photo.
  function galleryMatch(item, place, situation) {
    if (place && item.place !== place) return false;
    if (situation && item.situations.indexOf(situation) < 0) return false;
    return true;
  }

  function initGallery(doc) {
    var filters = doc.querySelector(".dk-gallery-filters");
    if (!filters) return;
    var place = filters.querySelector(".dk-gallery-place");
    var situation = filters.querySelector(".dk-gallery-situation");
    function apply() {
      Array.prototype.forEach.call(doc.querySelectorAll(".dk-photo-item"), function (li) {
        var item = { place: li.getAttribute("data-place") || "",
                     situations: (li.getAttribute("data-situation") || "").split("|") };
        li.hidden = !galleryMatch(item, place ? place.value : "", situation ? situation.value : "");
      });
    }
    [place, situation].forEach(function (select) {
      if (select) select.addEventListener("change", apply);
    });
    filters.hidden = false;
  }

  // True when the item has every chosen value; item maps a key to its values, an empty choice matches all.
  function listMatch(item, choices) {
    for (var key in choices) {
      if (choices[key] && (item[key] || []).indexOf(choices[key]) < 0) return false;
    }
    return true;
  }

  // Filters of the Situations and Conversations pages; a group whose items are all hidden is hidden too.
  function initListFilters(doc) {
    var bar = doc.querySelector(".dk-list-filters");
    if (!bar) return;
    var selects = bar.querySelectorAll(".dk-list-filter");
    function values(node, key) {
      var text = node.getAttribute("data-" + key) || "";
      return text ? text.split("|") : [];
    }
    function apply() {
      var choices = {};
      Array.prototype.forEach.call(selects, function (s) { choices[s.getAttribute("data-key")] = s.value; });
      Array.prototype.forEach.call(doc.querySelectorAll(".dk-filterable"), function (node) {
        var item = {};
        for (var key in choices) item[key] = values(node, key);
        node.hidden = !listMatch(item, choices);
      });
      Array.prototype.forEach.call(doc.querySelectorAll(".dk-group"), function (group) {
        group.hidden = !group.querySelector(".dk-filterable:not([hidden])");
      });
    }
    Array.prototype.forEach.call(selects, function (s) { s.addEventListener("change", apply); });
    bar.hidden = false;
  }

  dk.listMatch = listMatch;
  dk.initListFilters = initListFilters;
  dk.rowMatches = rowMatches;
  dk.galleryMatch = galleryMatch;
  dk.initGallery = initGallery;
  dk.initFilters = initFilters;
  dk.dateState = dateState;
  dk.initDates = initDates;
  dk.initDialogues = initDialogues;

  if (root.document && root.document.addEventListener) {
    root.document.addEventListener("DOMContentLoaded", function () {
      initFilters(root.document);
      initDates(root.document);
      initDialogues(root.document);
      initGallery(root.document);
      initListFilters(root.document);
    });
  }
})(typeof window !== "undefined" ? window : this);
