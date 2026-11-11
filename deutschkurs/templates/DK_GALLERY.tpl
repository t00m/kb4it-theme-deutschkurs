<%
    L = var['dk']['labels']
%>
<div class="dk-gallery dk-no-link">
% if var['places'] or var['situations']:
    <div class="dk-gallery-filters" hidden>
        <label>${L['place']}
            <select class="dk-gallery-place">
                <option value="">${L['all']}</option>
% for place in var['places']:
                <option value="${place}">${place}</option>
% endfor
            </select>
        </label>
        <label>${L['situation']}
            <select class="dk-gallery-situation">
                <option value="">${L['all']}</option>
% for name in var['situations']:
                <option value="${name}" lang="de">${name}</option>
% endfor
            </select>
        </label>
    </div>
% endif
    <ul class="dk-photos">
% for p in var['photos']:
        <li class="dk-photo-item" data-place="${p['place']}" data-situation="${p['situations']}">
            <a class="dk-photo" href="${p['href']}">
                <img loading="lazy" src="${p['src']}" alt="${p['title']}">
                <span class="dk-photo-title" lang="de">${p['title']}</span>
            </a>
        </li>
% endfor
    </ul>
</div>
