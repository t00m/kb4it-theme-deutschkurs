<%
    L = var['dk']['labels']
%>
<div class="dk-progress dk-no-link">
    <p><a class="uk-button uk-button-primary uk-button-small" href="practice.html">${L['practice']}</a></p>
    <div class="dk-section-title uk-h3">${L['progress_known']}</div>
    <noscript><p class="uk-alert uk-alert-warning">${L['progress_needs_js']}</p></noscript>
    <div id="dk-known"></div>
    <div class="dk-section-title uk-h3">${L['progress_cando']}</div>
    <ul class="dk-candos uk-list uk-list-divider">
% for c in var['candos']:
        <li class="dk-cando">
            <a href="${c['href']}" lang="de">${c['title']}</a> <span class="dk-note">${c['ticked']} / ${c['total']}</span>
            <progress class="uk-progress" value="${c['ticked']}" max="${c['total']}"></progress>
        </li>
% endfor
    </ul>
    <div class="dk-section-title uk-h3">${L['progress_wins']}</div>
% if var['wins']:
    <ul class="dk-wins uk-list uk-list-divider">
% for w in var['wins']:
        <li>
% if w['date']:
            <time datetime="${w['date']}">${w['date']}</time>
% endif
            <span class="dk-win-text" lang="de">${w['text']}</span>
            <a class="dk-from" href="${w['href']}" lang="de">${w['title']}</a>
        </li>
% endfor
    </ul>
% else:
    <p class="dk-note">${L['no_wins']}</p>
% endif
    <div class="dk-section-title uk-h3">${L['progress_patterns']}</div>
    <div id="dk-patterns"></div>
    <div class="dk-section-title uk-h3">${L['progress_days']}</div>
    <div id="dk-calendar"></div>
% if var['waiting']:
    <div class="dk-section-title uk-h3">${L['not_ready']}</div>
    <p class="dk-note">${L['not_ready_note']}</p>
    <ul class="dk-not-ready uk-list uk-list-divider">
% for w in var['waiting']:
        <li><a href="${w['href']}" lang="de">${w['title']}</a> <span class="dk-note">${w['reason']}</span></li>
% endfor
    </ul>
% endif
    <div id="dk-storage-off" hidden></div>
    ${var['scripts'] | n}
</div>
