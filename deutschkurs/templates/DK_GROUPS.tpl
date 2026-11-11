<%
    L = var['dk']['labels']
%>
<div class="dk-list dk-no-link">
${var.get('filters_html', '') | n}
% for found in var['groups']:
<%
    group, href, items = found[:3]
    points = found[3] if len(found) > 3 else []
%>
    <section class="dk-group">
% if href:
    <h2><a href="${href}" lang="de">${group}</a></h2>
% else:
    <h2>${group}</h2>
% endif
% if points:
    <p class="dk-points">${L['grammar_point']}:
% for title, link in points:
        <a href="${link}" lang="de">${title}</a>
% endfor
    </p>
% endif
    <ul class="dk-items uk-list uk-list-divider">
% for item in items:
% if var.get('filters_html'):
        <li class="dk-filterable" data-topic="${item['topics']}" data-level="${item['level']}" data-kind="${item['kind']}">
% else:
        <li>
% endif
            <a href="${item['href']}" lang="de">${item['title']}</a>
% if item['kind']:
            <span class="dk-badge dk-kind dk-kind-${item['kind']}">${item['kind']}</span>
% endif
% if item['level']:
            <span class="dk-badge dk-level">${item['level']}</span>
% endif
% if item['coverage']:
            <span class="dk-cover" title="${L['coverage']}">${item['coverage']}</span>
% endif
% if item.get('date'):
            <time datetime="${item['date']}">${item['date']}</time>
% endif
% if item['deadline']:
            <span class="dk-badge dk-deadline" data-date="${item['deadline']}" data-hide="past">${L['deadline']}: <time datetime="${item['deadline']}">${item['deadline']}</time></span>
% endif
        </li>
% endfor
    </ul>
    </section>
% endfor
</div>
