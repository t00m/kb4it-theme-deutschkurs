<%
    L = var['dk']['labels']
%>
<div class="dk-level dk-no-link">
    <p>${L['level_intro']}</p>
    <p>
        <a class="dk-practise-level uk-button uk-button-primary uk-button-small" href="${var['practice']}">${L['practise_level'].replace('{level}', var['level'])}</a>
        <a class="uk-button uk-button-default uk-button-small" href="Level.html">${L['all_levels']}</a>
    </p>
% for n, section in enumerate(var['sections'], 1):
    <section class="dk-study dk-study-${section['key']}" id="${section['key']}">
        <h2><span class="dk-step">${n}</span> ${section['label']} <span class="dk-count uk-badge">${section['count']}</span></h2>
% if section['hint']:
        <p class="dk-hint uk-text-small">${section['hint']}</p>
% endif
% if section['detailed']:
        <ol class="dk-items uk-list uk-list-divider uk-list-decimal">
% for item in section['items']:
            <li>
                <a href="${item['href']}" lang="de">${item['title']}</a>
% for name in item['situations']:
                <span class="dk-badge">${name}</span>
% endfor
% if item['coverage']:
                <span class="dk-cover" title="${L['coverage']}">${item['coverage']}</span>
% endif
            </li>
% endfor
        </ol>
% else:
% for heading, items in (section['groups'] or [('', section['items'])]):
% if heading:
        <h3 class="uk-h5 uk-margin-small-bottom">${heading}</h3>
% endif
        <ul class="dk-inline">
% for item in items:
            <li><a href="${item['href']}" lang="de" class="${item['css']}" title="${item['translation']}">${item['title']}</a></li>
% endfor
        </ul>
% endfor
% endif
    </section>
% endfor
</div>
