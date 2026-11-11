<div class="dk-list dk-no-link">
    <ul class="dk-situations uk-grid-small uk-child-width-1-1 uk-child-width-1-2@s" data-uk-grid>
% for situation in var['situations']:
        <li class="dk-situation">
            <div class="uk-card uk-card-default uk-card-small uk-card-body uk-border-rounded">
            <a class="dk-situation-title" href="${situation['href']}" lang="de">${situation['title']}</a>
            <dl class="dk-facts">
% for label, value in situation['facts']:
                <dt>${label}</dt><dd>${value}</dd>
% endfor
            </dl>
            </div>
        </li>
% endfor
    </ul>
</div>
