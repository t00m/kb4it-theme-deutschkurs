// deutschkurs: a simplified SM-2 scheduler (spec 7.3). Pure functions, no DOM.
(function (root) {
  "use strict";
  var dk = (root.Deutschkurs = root.Deutschkurs || {});
  var MIN_EASE = 1.3;

  function fresh() {
    return { due: "", interval: 0, ease: 2.5, reps: 0, lapses: 0, last: "", goods: 0 };
  }

  function two(n) { return (n < 10 ? "0" : "") + n; }

  // "YYYY-MM-DD" plus n days, in UTC so no time zone moves the day.
  function addDays(day, n) {
    var p = String(day).split("-");
    var date = new Date(Date.UTC(Number(p[0]), Number(p[1]) - 1, Number(p[2]) + n));
    return date.getUTCFullYear() + "-" + two(date.getUTCMonth() + 1) + "-" + two(date.getUTCDate());
  }

  function round2(x) { return Math.round(x * 100) / 100; }

  // A new state after one rating: "again", "hard" or "good". kind "mistake" keeps one day until three goods in a row.
  function rate(state, rating, today, kind) {
    var s = {}, key;
    var base = state || fresh();
    for (key in base) s[key] = base[key];
    if (rating === "again") {
      s.interval = 1;
      s.lapses += 1;
      s.ease = Math.max(MIN_EASE, round2(s.ease - 0.2));
      s.reps = 0;
      s.goods = 0;
    } else if (rating === "hard") {
      s.interval = Math.max(1, Math.round(s.interval * 1.2));
      s.ease = Math.max(MIN_EASE, round2(s.ease - 0.15));
      s.reps += 1;
      s.goods = 0;
    } else {
      if (s.reps === 0) s.interval = 1;
      else if (s.reps === 1) s.interval = 3;
      else s.interval = Math.max(1, Math.round(s.interval * s.ease));
      s.reps += 1;
      s.goods += 1;
    }
    if (kind === "mistake" && s.goods < 3) s.interval = 1;
    s.last = today;
    s.due = addDays(today, s.interval);
    return s;
  }

  // A card with no due day (never seen) is due.
  function isDue(state, today) {
    return !state || !state.due || state.due <= today;
  }

  dk.scheduler = { fresh: fresh, rate: rate, isDue: isDue, addDays: addDays };
})(typeof window !== "undefined" ? window : this);
