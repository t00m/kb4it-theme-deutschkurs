<%
    L = var['dk']['labels']
%>
<div class="dk-list dk-no-link">
% for group, href, items in var['groups']:
% if href:
    <h2><a href="${href}" lang="de">${group}</a></h2>
% else:
    <h2>${group}</h2>
% endif
    <ul class="dk-items">
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
% if item['deadline']:
            <span class="dk-badge dk-deadline" data-date="${item['deadline']}" data-hide="past">${L['deadline']}: <time datetime="${item['deadline']}">${item['deadline']}</time></span>
% endif
        </li>
% endfor
    </ul>
% endfor
</div>
