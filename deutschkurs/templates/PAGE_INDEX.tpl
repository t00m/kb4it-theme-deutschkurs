<%
    L = var['dk']['labels']
%>
<div class="dk-home dk-no-link">
    <ul class="dk-tiles">
% for label, href, count in var['counts']:
        <li><a class="dk-tile" href="${href}">
            <span class="dk-count">${count}</span>
            <span class="dk-tile-label">${label}</span>
        </a></li>
% endfor
    </ul>
% if var['latest']:
    <h2>${L['latest']}</h2>
    <ul class="dk-items">
% for title, href, kind in var['latest']:
        <li><a href="${href}" lang="de">${title}</a> <span class="dk-badge">${kind}</span></li>
% endfor
    </ul>
% endif
% if var['others']:
    <h2>${L['documents']}</h2>
    <ul class="dk-items">
% for title, href in var['others']:
        <li><a href="${href}">${title}</a></li>
% endfor
    </ul>
% endif
</div>
