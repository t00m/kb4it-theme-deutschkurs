<%
    L = var['dk']['labels']
%>
<div class="dk-home dk-no-link">
    <section class="dk-today uk-card uk-card-default uk-card-small uk-card-body uk-border-rounded uk-margin">
        <p class="uk-margin-remove">${L['today_intro']} <span class="dk-today-counts" hidden></span></p>
        <p class="uk-margin-small-top uk-margin-remove-bottom">
            <a class="dk-today-start uk-button uk-button-primary uk-button-small" href="practice.html">${L['practice']}</a>
            <a class="uk-button uk-button-default uk-button-small" href="progress.html">${L['progress']}</a>
        </p>
    </section>
    <ul class="dk-tiles uk-grid-small uk-child-width-1-2 uk-child-width-1-3@s uk-child-width-1-4@m" data-uk-grid>
% for label, href, count in var['counts']:
        <li><a class="dk-tile uk-card uk-card-default uk-card-small uk-card-body uk-card-hover uk-border-rounded" href="${href}">
            <span class="dk-count">${count}</span>
            <span class="dk-tile-label">${label}</span>
        </a></li>
% endfor
    </ul>
% if var['inbox']:
    <p class="dk-inbox-count uk-alert uk-alert-warning"><a href="inbox.html">${var['inbox']}</a></p>
% endif
% if var['coming']:
    <section class="dk-dated dk-coming-up">
        <h2>${L['coming_up']}</h2>
        <ul class="dk-items uk-list uk-list-divider">
% for title, href, date in var['coming']:
            <li data-date="${date}" data-days="${var['dk']['prepare_days']}" data-hide="past later"><a href="${href}" lang="de">${title}</a> <time datetime="${date}">${date}</time></li>
% endfor
        </ul>
    </section>
% endif
% if var['deadlines']:
    <section class="dk-dated dk-deadlines">
        <h2>${L['open_deadlines']}</h2>
        <ul class="dk-items uk-list uk-list-divider">
% for title, href, date in var['deadlines']:
            <li data-date="${date}" data-hide="past"><a href="${href}" lang="de">${title}</a> <time datetime="${date}">${date}</time></li>
% endfor
        </ul>
    </section>
% endif
% if var['latest']:
    <h2>${L['latest']}</h2>
    <ul class="dk-items uk-list uk-list-divider">
% for title, href, kind in var['latest']:
        <li><a href="${href}" lang="de">${title}</a> <span class="dk-badge">${kind}</span></li>
% endfor
    </ul>
% endif
% if var['others']:
    <h2>${L['documents']}</h2>
    <ul class="dk-items uk-list uk-list-divider">
% for title, href in var['others']:
        <li><a href="${href}">${title}</a></li>
% endfor
    </ul>
% endif
    ${var['scripts'] | n}
</div>
