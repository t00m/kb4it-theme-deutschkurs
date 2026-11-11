<%
    L = var['dk']['labels']
%>
<div class="dk-inbox dk-no-link">
    <ul class="dk-items">
% for i in var['items']:
        <li>
% if i['date']:
            <time datetime="${i['date']}">${i['date']}</time>
% endif
% if i['image']:
            <img class="dk-inbox-image" loading="lazy" src="${i['image']}" alt="" width="64">
% endif
% if i['href']:
            <a href="${i['href']}">${i['text']}</a> <span class="dk-badge">${L['to_process']}</span>
% else:
            <span lang="de">${i['text']}</span>
% endif
% if i['known']:
            <span class="dk-known">${L['already_in_course']}: <a href="${i['known']}" lang="de">${i['known_title']}</a></span>
% endif
        </li>
% endfor
    </ul>
</div>
