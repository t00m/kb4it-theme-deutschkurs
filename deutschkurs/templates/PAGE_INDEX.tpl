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
% if var['coming']:
    <section class="dk-dated dk-coming-up">
        <h2>${L['coming_up']}</h2>
        <ul class="dk-items">
% for title, href, date in var['coming']:
            <li data-date="${date}" data-days="${var['dk']['prepare_days']}" data-hide="past later"><a href="${href}" lang="de">${title}</a> <time datetime="${date}">${date}</time></li>
% endfor
        </ul>
    </section>
% endif
% if var['deadlines']:
    <section class="dk-dated dk-deadlines">
        <h2>${L['open_deadlines']}</h2>
        <ul class="dk-items">
% for title, href, date in var['deadlines']:
            <li data-date="${date}" data-hide="past"><a href="${href}" lang="de">${title}</a> <time datetime="${date}">${date}</time></li>
% endfor
        </ul>
    </section>
% endif
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
