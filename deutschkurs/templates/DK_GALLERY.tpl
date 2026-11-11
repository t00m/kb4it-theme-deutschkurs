<%
    L = var['dk']['labels']
%>
<div class="dk-gallery dk-no-link">
% if var['places'] or var['situations']:
    <div class="dk-gallery-filters" hidden>
        <div class="uk-flex uk-flex-wrap uk-margin">
        <label>${L['place']}
            <select class="dk-gallery-place uk-select uk-form-small">
                <option value="">${L['all']}</option>
% for place in var['places']:
                <option value="${place}">${place}</option>
% endfor
            </select>
        </label>
        <label>${L['situation']}
            <select class="dk-gallery-situation uk-select uk-form-small">
                <option value="">${L['all']}</option>
% for name in var['situations']:
                <option value="${name}" lang="de">${name}</option>
% endfor
            </select>
        </label>
        </div>
    </div>
% endif
    <ul class="dk-photos uk-grid-small uk-child-width-1-2 uk-child-width-1-3@s uk-child-width-1-4@m" data-uk-grid>
% for p in var['photos']:
        <li class="dk-photo-item" data-place="${p['place']}" data-situation="${p['situations']}">
            <a class="dk-photo" href="${p['href']}">
                <span class="uk-card uk-card-default uk-card-hover uk-border-rounded uk-display-block">
                    <span class="uk-card-media-top uk-display-block"><img loading="lazy" src="${p['src']}" alt="${p['title']}"></span>
                    <span class="dk-photo-title uk-card-body uk-card-small uk-display-block" lang="de">${p['title']}</span>
                </span>
            </a>
        </li>
% endfor
    </ul>
</div>
