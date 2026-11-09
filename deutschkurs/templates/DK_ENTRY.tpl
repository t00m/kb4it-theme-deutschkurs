<%
    dk = var['dk']
    c = dk['card']
    L = dk['labels']
%>
<main class="dk-main dk-entry dk-type-${c['kind'].lower()}">
    <section class="dk-card">
        <div class="dk-card-head">
            <h1 class="dk-headline ${c['headline_class']}" lang="de">${c['headline']}</h1>
            <button type="button" class="dk-listen" data-say="${c['say']}">${L['listen']}</button>
        </div>
% if c['translation']:
        <p class="dk-translation" lang="${dk['native']}">${c['translation']}</p>
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
    <div class="dk-body">
        ${var['source_html'] | n}
    </div>
</main>
