// deutschkurs: the Practice page and the Today block of the home page. DOM only; the logic is in
// answer.js, scheduler.js, practice-core.js and store.js.
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});
  var doc = root.document;

  function localDay(now) {
    function two(n) { return (n < 10 ? "0" : "") + n; }
    return now.getFullYear() + "-" + two(now.getMonth() + 1) + "-" + two(now.getDate());
  }

  function labels() {
    var node = doc.getElementById("dk-practice-labels");
    try { return node ? JSON.parse(node.textContent) : {}; } catch (e) { return {}; }
  }

  function fill(text, values) {
    return String(text || "").replace(/\{(\w+)\}/g, function (m, key) {
      return values[key] !== undefined ? values[key] : m;
    });
  }

  function el(tag, attrs, children) {
    var node = doc.createElement(tag);
    var key;
    for (key in attrs || {}) {
      if (key === "text") node.textContent = attrs[key];
      else if (key === "className") node.className = attrs[key];
      else node.setAttribute(key, attrs[key]);
    }
    (children || []).forEach(function (child) { if (child) node.appendChild(child); });
    return node;
  }

  function storage() {
    try { return root.localStorage; } catch (e) { return null; }
  }

  // Listen and Slow buttons; speech.js handles their clicks.
  function listen(text, L, me) {
    var css = "uk-button uk-button-default uk-button-small";
    var mine = me ? "true" : "false";
    return el("span", { className: "dk-say" }, [
      el("button", { type: "button", className: "dk-listen " + css, "data-say": text, "data-me": mine,
                     text: L.listen || "Listen" }),
      doc.createTextNode(" "),
      el("button", { type: "button", className: "dk-listen dk-slow " + css, "data-say": text, "data-me": mine,
                     "data-rate": "slow", text: L.slow || "Slow" })]);
  }

  // A recording: one Listen button that plays the file, and the real badge.
  function recording(src, L) {
    return el("span", { className: "dk-say" }, [
      el("button", { type: "button", className: "dk-listen uk-button uk-button-default uk-button-small",
                     "data-audio": src, text: L.listen || "Listen" }),
      doc.createTextNode(" "),
      el("span", { className: "dk-badge dk-real", text: L.real_audio || "real" })]);
  }

  // State shared by the Today block and the Practice page.
  function setup() {
    var data = root.DEUTSCHKURS_DATA;
    if (!data || !dk.practice || !dk.store) return null;
    var store = dk.store.open(storage(), data.site);
    return { data: data, store: store, cards: dk.practice.cards(data), today: localDay(new Date()), L: labels() };
  }

  function initToday(ctx) {
    var block = doc.querySelector(".dk-today");
    if (!block || !ctx) return;
    var c = dk.practice.counts(ctx.cards, ctx.store.cards(), ctx.today, ctx.data);
    var counts = block.querySelector(".dk-today-counts");
    counts.textContent = fill(ctx.L.due_new, { due: c.due, "new": c.fresh });
    counts.hidden = false;
    block.querySelector(".dk-today-start").setAttribute("href", "practice.html#session=daily");
  }

  function initPractice(ctx) {
    var area = doc.getElementById("dk-practice-card");
    if (!area) return;
    if (!ctx) {
      doc.getElementById("dk-no-data").hidden = false;
      return;
    }
    var L = ctx.L;
    if (!ctx.store.ok) doc.getElementById("dk-storage-off").hidden = false;
    var queue = [], position = 0, done = 0;

    function filters() {
      var found = {};
      Array.prototype.forEach.call(doc.querySelectorAll("[data-filter]"), function (select) {
        if (select.value) found[select.getAttribute("data-filter")] = select.value;
      });
      return found;
    }

    function start(kind, chosen) {
      queue = dk.practice.session(kind, ctx.cards, ctx.store.cards(), ctx.data, ctx.today, chosen || {});
      position = 0;
      done = 0;
      area.hidden = false;
      show();
      if (area.scrollIntoView) area.scrollIntoView();
    }

    function finish(card, rating) {
      var states = ctx.store.cards();
      var next = dk.scheduler.rate(states[card.id], rating, ctx.today, card.kind);
      ctx.store.save(card.id, next);
      ctx.store.studied(ctx.today);
      done += 1;
      position += 1;
      show();
    }

    function ratingButtons(card) {
      return el("p", { className: "dk-ratings" }, ["again", "hard", "good"].map(function (rating) {
        var button = el("button", { type: "button", className: "uk-button uk-button-default dk-rate-" + rating,
                                    text: L[rating] });
        button.addEventListener("click", function () { finish(card, rating); });
        return button;
      }));
    }

    function nextButton(card, rating) {
      var button = el("button", { type: "button", className: "uk-button uk-button-primary", text: L.next });
      button.addEventListener("click", function () { finish(card, rating); });
      return button;
    }

    function diffNode(ops) {
      return el("p", { className: "dk-diff", lang: "de" }, ops.map(function (op) {
        return el(op.op === "same" ? "span" : op.op === "add" ? "ins" : "del", { text: op.text });
      }));
    }

    function verdict(result, card, shown) {
      var box = el("div", { className: "dk-verdict dk-verdict-" + result.result });
      var word = result.result === "good" ? L.right : result.result === "hard" ? L.almost : L.not_yet;
      box.appendChild(el("p", { className: "dk-verdict-word", text: word }));
      box.appendChild(el("p", {}, [el("span", { className: "uk-text-muted", text: L.expected + ": " }),
        el("span", { lang: "de", text: shown.answer }), shown.answer ? listen(shown.answer, L) : null]));
      if (result.result !== "good" && result.diff.length) box.appendChild(diffNode(result.diff));
      if (shown.sentence) box.appendChild(el("p", { lang: "de", text: shown.sentence }));
      box.appendChild(nextButton(card, result.result));
      return box;
    }

    function typed(card, shown, body) {
      var input = el("input", { type: "text", className: "uk-input dk-answer", autocomplete: "off",
                                autocapitalize: "off", spellcheck: "false", lang: "de", "aria-label": L.your_answer,
                                placeholder: L.your_answer });
      var button = el("button", { type: "submit", className: "uk-button uk-button-primary", text: L.check });
      var form = el("form", { className: "dk-answer-form uk-flex" }, [input, button]);
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var options = {};
        var key;
        for (key in card.options) options[key] = card.options[key];
        options.alternatives = shown.alternatives || [];
        var result = dk.answer.check(input.value, shown.answer, options);
        input.disabled = true;
        button.disabled = true;
        body.appendChild(verdict(result, card, shown));
      });
      body.appendChild(form);
      input.focus();
    }

    function choice(card, body) {
      var row = el("p", { className: "dk-choices" }, card.choices.map(function (option) {
        var css = { der: "dk-m", die: "dk-f", das: "dk-n" }[option] || "";
        var button = el("button", { type: "button", className: "uk-button uk-button-default uk-button-large " + css,
                                    text: option });
        button.addEventListener("click", function () {
          Array.prototype.forEach.call(row.querySelectorAll("button"), function (b) { b.disabled = true; });
          var result = { result: option === card.answer ? "good" : "again", diff: [] };
          body.appendChild(verdict(result, card, { answer: card.answer + " " + card.prompt }));
        });
        return button;
      }));
      body.appendChild(row);
    }

    function self(card, shown, body) {
      body.appendChild(el("p", { className: "uk-text-small uk-text-muted", text: L.say_aloud }));
      var reveal = el("button", { type: "button", className: "uk-button uk-button-primary", text: L.reveal });
      reveal.addEventListener("click", function () {
        reveal.remove();
        var german = card.exercise !== "to_native";
        body.appendChild(el("p", { className: "dk-revealed", lang: german ? "de" : ctx.data.settings.native },
                            [el("span", { text: shown.answer }), german ? listen(shown.answer, L) : null]));
        body.appendChild(ratingButtons(card));
      });
      body.appendChild(reveal);
    }

    // Roleplay: the other turns are shown and spoken; for my turns the translation, then the German.
    function roleplay(card, body) {
      var list = el("ol", { className: "dk-dialogue" });
      body.appendChild(list);
      var turn = 0;
      // Show the turns of the other speaker up to the next turn of the learner and speak them in a row.
      function step() {
        var spoken = [];
        while (turn < card.turns.length && !card.turns[turn].me) {
          var other = card.turns[turn];
          turn += 1;
          list.appendChild(el("li", { className: "dk-turn dk-other" }, [
            el("span", { className: "dk-speaker", text: other.speaker }),
            el("span", { lang: "de", text: other.german }),
            other.audio ? recording(other.audio, L) : listen(other.german, L, false)]));
          spoken.push(other.audio ? { audio: other.audio } : { text: other.german, me: false });
        }
        if (spoken.length && dk.speech && dk.speech.sayAll) dk.speech.sayAll(spoken);
        if (turn >= card.turns.length) {
          body.appendChild(ratingButtons(card));
          return;
        }
        var t = card.turns[turn];
        turn += 1;
        var item = el("li", { className: "dk-turn dk-me" }, [
          el("span", { className: "dk-speaker", text: L.your_turn }),
          el("span", { className: "dk-tr", text: t.translation })]);
        var reveal = el("button", { type: "button", className: "uk-button uk-button-default uk-button-small",
                                    text: L.reveal });
        reveal.addEventListener("click", function () {
          reveal.remove();
          item.appendChild(el("span", { className: "dk-de", lang: "de", text: t.german }));
          item.appendChild(t.audio ? recording(t.audio, L) : listen(t.german, L, true));
          step();
        });
        item.appendChild(reveal);
        list.appendChild(item);
      }
      body.appendChild(el("p", { className: "uk-text-small uk-text-muted", text: L.say_aloud }));
      step();
    }

    function show() {
      area.textContent = "";
      if (!queue.length) {
        area.appendChild(el("p", { text: L.no_cards }));
        return;
      }
      if (position >= queue.length) {
        area.appendChild(el("p", { className: "dk-session-done", text: fill(L.session_done, { n: done }) }));
        return;
      }
      var card = queue[position];
      var state = ctx.store.cards()[card.id];
      var shown = dk.practice.view(card, state);
      area.appendChild(el("p", { className: "uk-text-small uk-text-muted",
                                 text: fill(L.card_of, { n: position + 1, total: queue.length }) }));
      area.appendChild(el("h2", { className: "uk-h4 dk-exercise", text: L["exercise_" + card.exercise] }));
      var germanPrompt = ["article", "plural", "to_native", "perfekt", "separable", "cloze", "mistake", "roleplay"]
        .indexOf(card.exercise) >= 0;
      var prompt = el("p", { className: "dk-prompt", lang: germanPrompt ? "de" : ctx.data.settings.native },
                      [el("span", { text: shown.prompt })]);
      if (germanPrompt && card.exercise !== "roleplay" && card.exercise !== "cloze" && card.exercise !== "separable") {
        prompt.appendChild(listen(shown.prompt, L));
      }
      area.appendChild(prompt);
      if (shown.translation && card.exercise !== "to_target" && card.exercise !== "to_native") {
        area.appendChild(el("p", { className: "dk-hint uk-text-muted", text: shown.translation }));
      }
      var body = el("div", { className: "dk-card-body" });
      area.appendChild(body);
      if (card.exercise === "roleplay") roleplay(card, body);
      else if (card.check === "choice") choice(card, body);
      else if (card.check === "self") self(card, shown, body);
      else typed(card, shown, body);
    }

    Array.prototype.forEach.call(doc.querySelectorAll(".dk-session"), function (button) {
      button.addEventListener("click", function () {
        var kind = button.getAttribute("data-session");
        start(kind, kind === "free" ? filters() : {});
      });
    });

    doc.getElementById("dk-export").addEventListener("click", function () {
      var text = dk.store.exportJson(ctx.store, ctx.data.site, ctx.today);
      var link = el("a", { href: URL.createObjectURL(new Blob([text], { type: "application/json" })),
                           download: "deutschkurs-progress-" + ctx.today + ".json" });
      doc.body.appendChild(link);
      link.click();
      link.remove();
    });

    var importer = doc.getElementById("dk-import");
    importer.addEventListener("change", function () {
      var file = importer.files && importer.files[0];
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function () {
        var known = ctx.cards.map(function (c) { return c.id; });
        var local = { cards: ctx.store.cards(), days: ctx.store.days() };
        var result = dk.store.merge(local, String(reader.result || ""), known);
        var out = doc.getElementById("dk-import-result");
        if (result.error) {
          out.textContent = L.import_error;
        } else {
          ctx.store.replace(result.cards, result.days);
          out.textContent = fill(L.imported, { merged: result.merged, skipped: result.skipped });
        }
        importer.value = "";
      };
      reader.readAsText(file);
    });

    // practice.html#session=daily starts a session; #situation=<title> opens free practice for it.
    var hash = String(root.location && root.location.hash || "").replace(/^#/, "");
    var match = /^(session|situation)=(.*)$/.exec(hash);
    if (match) {
      var value = "";
      try { value = decodeURIComponent(match[2]); } catch (e) { value = match[2]; }
      if (match[1] === "session") start(value, {});
      else {
        var select = doc.querySelector('[data-filter="situation"]');
        if (select) select.value = value;
        start("free", { situation: value });
      }
    }
  }

  dk.practicePage = { localDay: localDay, fill: fill };

  if (doc && doc.addEventListener) {
    doc.addEventListener("DOMContentLoaded", function () {
      var ctx = setup();
      initToday(ctx);
      initPractice(ctx);
    });
  }
})(typeof window !== "undefined" ? window : this);
