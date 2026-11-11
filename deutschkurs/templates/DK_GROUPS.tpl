<%
    L = var['dk']['labels']
%>
<div class="dk-list dk-no-link">
% for found in var['groups']:
<%
    group, href, items = found[:3]
    points = found[3] if len(found) > 3 else []
%>
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
        <li>
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
% endfor
</div>
