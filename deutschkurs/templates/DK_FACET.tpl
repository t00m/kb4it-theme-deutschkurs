<div class="dk-list dk-no-link">
    <ul class="dk-items">
% for value, href, count in var['values']:
        <li><a href="${href}">${value}</a> <span class="dk-count">${count}</span></li>
% endfor
    </ul>
</div>
