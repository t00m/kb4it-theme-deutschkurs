<div class="dk-list dk-no-link">
% for group, items in var['groups']:
    <h2>${group}</h2>
    <ul class="dk-items">
% for title, href, level in items:
        <li><a href="${href}" lang="de">${title}</a> <span class="dk-badge dk-level">${level}</span></li>
% endfor
    </ul>
% endfor
</div>
