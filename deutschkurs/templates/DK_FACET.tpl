<div class="dk-list dk-no-link">
    <ul class="dk-items uk-list uk-list-divider">
% for value, href, count in var['values']:
        <li><a href="${href}">${value}</a> <span class="dk-count uk-badge">${count}</span></li>
% endfor
    </ul>
</div>
