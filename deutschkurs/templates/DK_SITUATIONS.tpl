<div class="dk-list dk-no-link">
    <ul class="dk-situations">
% for situation in var['situations']:
        <li class="dk-situation">
            <a class="dk-situation-title" href="${situation['href']}" lang="de">${situation['title']}</a>
            <dl class="dk-facts">
% for label, value in situation['facts']:
                <dt>${label}</dt><dd>${value}</dd>
% endfor
            </dl>
        </li>
% endfor
    </ul>
</div>
