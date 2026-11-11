// deutschkurs: search dialog. "/" or Ctrl+K opens it; the search field gets the focus.
(function () {
  "use strict";
  var modal = document.getElementById("dk-search");
  if (!modal || !window.UIkit) return;
  UIkit.util.on(modal, "shown", function () {
    var input = document.getElementById("kb4it-search-input");
    if (input) input.focus();
  });
  document.addEventListener("keydown", function (e) {
    // Keys typed in a field are left alone: Ctrl+K inserts a link in the Add page editor.
    var target = e.target;
    var typing = target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName);
    var slash = e.key === "/" && !e.ctrlKey && !e.metaKey && !e.altKey;
    var ctrlK = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k";
    if (!typing && (slash || ctrlK)) {
      e.preventDefault();
      UIkit.modal(modal).show();
    }
  });
})();
