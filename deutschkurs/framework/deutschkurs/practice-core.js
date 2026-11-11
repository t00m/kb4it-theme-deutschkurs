// deutschkurs: practice cards and sessions (spec 7.2 and 7.4). Pure functions, no DOM.
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});
  // Order of the exercises of one entry: understanding before producing.
  var ORDER = ["to_native", "article", "plural", "to_target", "perfekt", "separable", "cloze", "mistake", "gap",
               "roleplay"];
  var ARTICLES = ["der", "die", "das"];
  var PERFEKT = { haben: "hat", sein: "ist" };
  var GAP = "___";

  function has(list, item) { return (list || []).indexOf(item) >= 0; }

  // The German of an entry as it is learnt: nouns with their article.
  function german(entry) {
    if (entry.type === "Word" && entry.noun) {
      if (entry.plural_only) return "die " + entry.title;
      if (entry.article) return entry.article + " " + entry.title;
    }
    return entry.title;
  }

  function withArticle(entry, word) {
    if (!(entry.type === "Word" && entry.noun)) return word;
    if (/^(der|die|das)\s/i.test(word)) return word;
    return (entry.plural_only ? "die" : entry.article) + " " + word;
  }

  function card(entry, exercise, fields) {
    var c = { id: exercise + ":" + entry.id, exercise: exercise, entry: entry.id, kind: "", check: "typed",
              prompt: "", answer: "", alternatives: [], options: {}, choices: [], translation: entry.translation,
              items: [], turns: [] };
    for (var key in fields) c[key] = fields[key];
    return c;
  }

  function cardsOf(entry, sentences) {
    var found = [];
    var t = entry.type;
    var noun = t === "Word" && entry.noun;
    if (t === "Word" || t === "Verb" || t === "Chunk") {
      found.push(card(entry, "to_native", { check: "self", prompt: german(entry), answer: entry.translation }));
      found.push(card(entry, "to_target", {
        prompt: entry.translation, answer: german(entry),
        alternatives: (entry.regional || []).map(function (w) { return withArticle(entry, w); })
          .concat(entry.variants || []),
        options: { noun: noun, article: noun } }));
      var rows = sentences.filter(function (r) { return r.entry === entry.id; });
      if (rows.length) {
        found.push(card(entry, "cloze", { items: rows, alternatives: entry.forms || [], options: { noun: noun } }));
      }
    }
    if (noun && !entry.plural_only && has(ARTICLES, entry.article)) {
      found.push(card(entry, "article", { check: "choice", prompt: entry.title, answer: entry.article,
                                          choices: ARTICLES.slice() }));
    }
    if (noun && entry.plural && entry.plural !== "none" && entry.plural !== "-") {
      found.push(card(entry, "plural", { prompt: german(entry), answer: entry.plural,
                                         options: { noun: true, article: /^(der|die|das)\s/.test(entry.plural) } }));
    }
    if (t === "Verb" && entry.participle && (entry.auxiliary || []).length) {
      var forms = entry.auxiliary.filter(function (a) { return PERFEKT[a]; })
        .map(function (a) { return PERFEKT[a] + " " + entry.participle; });
      if (forms.length) {
        found.push(card(entry, "perfekt", { prompt: entry.title, answer: forms[0], alternatives: forms.slice(1) }));
      }
    }
    if (t === "Verb" && (entry.separable || []).length) {
      found.push(card(entry, "separable", { items: entry.separable }));
    }
    if (t === "Mistake" && entry.right) {
      found.push(card(entry, "mistake", { kind: "mistake", prompt: entry.wrong, answer: entry.right }));
    }
    if (t === "Gap" && entry.german) {
      found.push(card(entry, "gap", { check: "self", prompt: entry.wanted, answer: entry.german }));
    }
    if (t === "Conversation" && (entry.turns || []).some(function (turn) { return turn.me; })) {
      found.push(card(entry, "roleplay", { check: "self", prompt: entry.title, turns: entry.turns }));
    }
    found.sort(function (a, b) { return ORDER.indexOf(a.exercise) - ORDER.indexOf(b.exercise); });
    return found;
  }

  // Every card the data allows; entries that are not ready give none (spec 7.4).
  function cards(data) {
    var sentences = (data && data.sentences) || [];
    var found = [];
    ((data && data.entries) || []).forEach(function (entry) {
      if (entry.ready) found = found.concat(cardsOf(entry, sentences));
    });
    return found;
  }

  function blank(text, spans) {
    var out = "", pos = 0;
    spans.forEach(function (span) {
      out += text.slice(pos, span[0]) + GAP;
      pos = span[1];
    });
    return out + text.slice(pos);
  }

  // What to show for a card this time: cloze and separable take the next sentence each time.
  function view(c, state) {
    var shown = { prompt: c.prompt, answer: c.answer, alternatives: c.alternatives, translation: c.translation };
    if (!c.items.length) return shown;
    var turn = state ? (state.reps || 0) + (state.lapses || 0) : 0;
    var item = c.items[turn % c.items.length];
    if (c.exercise === "cloze") {
      shown.prompt = blank(item.german, [[item.start, item.end]]);
      shown.answer = item.german.slice(item.start, item.end);
    } else {
      shown.prompt = blank(item.german, item.parts);
      shown.answer = item.parts.map(function (p) { return item.german.slice(p[0], p[1]); }).join(" ");
    }
    shown.translation = item.translation;
    shown.sentence = item.german;
    return shown;
  }

  function byId(data) {
    var map = {};
    ((data && data.entries) || []).forEach(function (e) { map[e.id] = e; });
    return map;
  }

  function addDays(day, n) {
    return dk.scheduler ? dk.scheduler.addDays(day, n) : day;
  }

  // Titles of situations whose next time is today or within prepare_days.
  function comingUp(data, today) {
    var days = (data.settings && data.settings.prepare_days) || 7;
    var limit = addDays(today, days);
    return (data.situations || []).filter(function (s) {
      return s.next_time && s.next_time >= today && s.next_time <= limit;
    }).map(function (s) { return s.title; });
  }

  function seen(state) { return !!(state && state.last); }

  function dueCards(list, states, today) {
    return list.filter(function (c) { return seen(states[c.id]) && states[c.id].due <= today; })
      .sort(function (a, b) { return states[a.id].due < states[b.id].due ? -1 : states[a.id].due > states[b.id].due ? 1 : 0; });
  }

  // New cards, one entry after another: coming-up situations first, then the newest entries.
  function newCards(list, states, data, today) {
    var entries = byId(data), soon = comingUp(data, today);
    var fresh = list.filter(function (c) { return !seen(states[c.id]) && c.exercise !== "roleplay"; });
    var groups = {}, order = [];
    fresh.forEach(function (c) {
      if (!groups[c.entry]) { groups[c.entry] = []; order.push(c.entry); }
      groups[c.entry].push(c);
    });
    function urgent(id) {
      return (entries[id].situations || []).some(function (s) { return has(soon, s); }) ? 0 : 1;
    }
    order.sort(function (a, b) {
      var ea = entries[a], eb = entries[b];
      if (urgent(a) !== urgent(b)) return urgent(a) - urgent(b);
      if ((ea.date || "") !== (eb.date || "")) return (ea.date || "") > (eb.date || "") ? -1 : 1;
      return ea.title < eb.title ? -1 : ea.title > eb.title ? 1 : 0;
    });
    var out = [], round = 0, added = true;
    while (added) {
      added = false;
      order.forEach(function (id) {
        if (groups[id][round]) { out.push(groups[id][round]); added = true; }
      });
      round += 1;
    }
    return out;
  }

  // The conversation of the day: a coming-up situation first, else the least recently practised.
  function conversation(list, states, data, today) {
    var entries = byId(data), soon = comingUp(data, today);
    var plays = list.filter(function (c) { return c.exercise === "roleplay"; });
    if (!plays.length) return null;
    var urgent = plays.filter(function (c) {
      return (entries[c.entry].situations || []).some(function (s) { return has(soon, s); });
    });
    var pool = urgent.length ? urgent : plays;
    pool = pool.slice().sort(function (a, b) {
      var la = (states[a.id] && states[a.id].last) || "", lb = (states[b.id] && states[b.id].last) || "";
      return la < lb ? -1 : la > lb ? 1 : 0;
    });
    return pool[0];
  }

  // Mistake cards of the patterns with the most lapses.
  function weakMistakes(list, states, data) {
    var entries = byId(data), lapses = {};
    var mistakes = list.filter(function (c) { return c.exercise === "mistake"; });
    mistakes.forEach(function (c) {
      var pattern = entries[c.entry].pattern || "";
      lapses[pattern] = (lapses[pattern] || 0) + ((states[c.id] && states[c.id].lapses) || 0);
    });
    var top = Object.keys(lapses).filter(function (p) { return lapses[p] > 0; })
      .sort(function (a, b) { return lapses[b] - lapses[a]; }).slice(0, 2);
    return mistakes.filter(function (c) { return has(top, entries[c.entry].pattern || ""); });
  }

  function matches(entry, filters) {
    if (filters.level && entry.level !== filters.level) return false;
    if (filters.type && entry.type !== filters.type) return false;
    if (filters.situation && !has(entry.situations, filters.situation)) return false;
    if (filters.topic && !has(entry.topics, filters.topic)) return false;
    return true;
  }

  function unique(list) {
    var seenIds = {}, out = [];
    list.forEach(function (c) {
      if (c && !seenIds[c.id]) { seenIds[c.id] = true; out.push(c); }
    });
    return out;
  }

  // The cards of one session: "daily", "short", "weekly" or "free" (spec 7.4).
  function session(kind, list, states, data, today, filters) {
    var s = (data && data.settings) || {};
    states = states || {};
    list = list || [];
    if (!list.length) return [];
    var due = dueCards(list, states, today);
    if (kind === "short") return due.slice(0, 15);
    if (kind === "free") {
      var entries = byId(data);
      var chosen = list.filter(function (c) { return matches(entries[c.entry], filters || {}); });
      return unique(dueCards(chosen, states, today).concat(chosen));
    }
    var reviews = due.slice(0, s.daily_reviews || 40);
    var talk = conversation(list, states, data, today);
    var fresh = newCards(list, states, data, today);
    if (kind === "weekly") {
      return unique(reviews.concat([talk], weakMistakes(list, states, data), fresh.slice(0, s.weekly_new || 10)));
    }
    return unique(reviews.concat([talk], fresh.slice(0, s.daily_new || 5)));
  }

  function counts(list, states, today, data) {
    var s = (data && data.settings) || {};
    return { due: dueCards(list || [], states || {}, today).length,
             fresh: Math.min(newCards(list || [], states || {}, data || {}, today).length, s.daily_new || 5) };
  }

  dk.practice = { cards: cards, view: view, session: session, counts: counts, german: german,
                  comingUp: comingUp };
})(typeof window !== "undefined" ? window : this);
