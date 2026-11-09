// deutschkurs: shared namespace and the filter of list tables.
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});

  // True when a row's cells match the text and every column filter.
  function rowMatches(cells, text, columns) {
    var needle = (text || "").trim().toLowerCase();
    if (needle && cells.join(" ").toLowerCase().indexOf(needle) < 0) return false;
    for (var key in columns) {
      if (columns[key] && cells[key] !== columns[key]) return false;
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

  dk.rowMatches = rowMatches;
  dk.initFilters = initFilters;

  if (root.document && root.document.addEventListener) {
    root.document.addEventListener("DOMContentLoaded", function () { initFilters(root.document); });
  }
})(typeof window !== "undefined" ? window : this);
