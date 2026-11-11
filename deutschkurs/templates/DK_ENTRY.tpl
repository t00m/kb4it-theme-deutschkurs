<%
    dk = var['dk']
    c = dk['card']
    x = dk['extras']
    L = dk['labels']
    unverified = ' dk-unverified' if c['unverified'] else ''
    hint = c['hint_attr']
%>
<%def name="sentences(items)">
        <ul class="dk-occurrences">
% for o in items:
            <li>
                <span class="dk-de" lang="de">${o['german']}</span>
                <button type="button" class="dk-listen" data-say="${o['german']}">${L['listen']}</button>
% if o['translation']:
                <span class="dk-tr" lang="${dk['native']}">${o['translation']}</span>
% endif
                <a class="dk-from" href="${o['href']}">${o['title']}</a>
% if o['kind']:
                <span class="dk-badge dk-kind dk-kind-${o['kind']}">${o['kind']}</span>
% endif
            </li>
% endfor
        </ul>
</%def>
<main class="dk-main dk-entry dk-type-${c['kind'].lower()}">
    <section class="dk-card">
        <div class="dk-card-head">
            <h1 class="dk-headline ${c['headline_class']}${unverified}" lang="de"${hint | n}>${c['headline']}</h1>
% if c['say']:
            <button type="button" class="dk-listen" data-say="${c['say']}">${L['listen']}</button>
% endif
        </div>
% if c['translation']:
        <p class="dk-translation${unverified}" lang="${dk['native']}"${hint | n}>${c['translation']}</p>
% endif
        <p class="dk-badges">
% for css, text, href in c['badges']:
% if href:
            <a class="${css}" href="${href}">${text}</a>
% else:
            <span class="${css}">${text}</span>
% endif
% endfor
        </p>
% if c['facts'] or c['links']:
        <dl class="dk-facts">
% for label, text in c['facts']:
            <dt>${label}</dt><dd>${text}</dd>
% endfor
% for label, items in c['links']:
            <dt>${label}</dt>
            <dd>
% for title, href in items:
% if href:
                <a href="${href}">${title}</a>
% else:
                <span>${title}</span>
% endif
% endfor
            </dd>
% endfor
        </dl>
% endif
    </section>
% if x['deadline']:
    <p class="dk-banner dk-deadline" data-date="${x['deadline']}" data-hide="past">${L['deadline']}: <time datetime="${x['deadline']}">${x['deadline']}</time></p>
% endif
% if x['next_time']:
    <p class="dk-banner dk-coming" data-date="${x['next_time']}" data-days="${var['dk']['prepare_days']}" data-hide="past later">${L['coming_up']}: <time datetime="${x['next_time']}">${x['next_time']}</time></p>
% endif
    <div class="dk-body">
        ${var['source_html'] | n}
    </div>
% if x['see_inbox']:
    <p class="dk-see-inbox"><a href="inbox.html">${L['see_inbox']}</a></p>
% endif
% for label, items in x['related']:
    <section class="dk-related">
        <h2>${label}</h2>
        <ul class="dk-items">
% for title, href, kind in items:
            <li>
                <a href="${href}">${title}</a>
% if kind:
                <span class="dk-badge dk-kind dk-kind-${kind}">${kind}</span>
% endif
            </li>
% endfor
        </ul>
    </section>
% endfor
% if x['occurrences']:
    <section class="dk-where">
        <h2>${L['where']}</h2>
        ${sentences(x['occurrences'])}
% if x['more']:
        <p class="dk-more">${L['more'].replace('{n}', str(x['more']))}</p>
% endif
    </section>
% endif
% if x['candidates']:
    <section class="dk-candidates">
        <h2>${L['in_texts']}</h2>
        <p class="dk-note">${L['candidates']}</p>
        ${sentences(x['candidates'])}
% if x['more_candidates']:
        <p class="dk-more">${L['more'].replace('{n}', str(x['more_candidates']))}</p>
% endif
    </section>
% endif
% if x['coverage'] is not None and x['coverage'].total:
    <section class="dk-coverage">
        <h2>${L['coverage']}</h2>
        <p>${x['coverage'].covered} / ${x['coverage'].total} (${x['coverage'].percent} %)</p>
% if x['coverage'].missing:
        <h3>${L['missing_words']}</h3>
        <ul class="dk-missing" lang="de">
% for word in x['coverage'].missing:
            <li>${word}</li>
% endfor
        </ul>
% endif
    </section>
% endif
</main>
