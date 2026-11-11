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

// deutschkurs: "Edit in the editor" opens add.html with the file name and its Markdown in the address,
// as the KB4IT editor reads them (add.html#edit=<file>&text=<markdown>); it works from file:// too.
(function () {
  "use strict";
  document.addEventListener("click", function (event) {
    var link = event.target.closest ? event.target.closest("[data-kb-edit]") : null;
    var source = document.getElementById("dk-source-text");
    if (!link || !source || event.ctrlKey || event.metaKey || event.shiftKey) return;
    event.preventDefault();
    window.location.href = link.getAttribute("href") + "#edit=" + encodeURIComponent(link.getAttribute("data-kb-edit")) +
      "&text=" + encodeURIComponent(source.value);
  });
})();
