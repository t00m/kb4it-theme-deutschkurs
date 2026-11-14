<%
    L = var['dk']['labels']
%>
<div class="dk-levels dk-no-link">
    <p>${L['levels_intro']}</p>
    <section class="dk-how uk-card uk-card-default uk-card-small uk-card-body uk-border-rounded uk-margin">
        <h2 class="uk-h4 uk-margin-small-bottom">${L['how_to_study']}</h2>
        <ol class="uk-margin-remove-bottom">
% for n in (1, 2, 3, 4):
            <li>${L['study_how_%d' % n]}</li>
% endfor
        </ol>
    </section>
    <ul class="dk-level-cards uk-grid-small uk-child-width-1-2@s" data-uk-grid>
% for card in var['cards']:
        <li>
            <div class="dk-level-card uk-card uk-card-default uk-card-small uk-card-body uk-border-rounded${' dk-mine' if card['mine'] else ''}">
                <h2 class="uk-margin-remove"><a href="${card['href']}">${card['level']}</a>
% if card['mine']:
                    <span class="dk-badge dk-your-level">${L['your_level']}</span>
% endif
                </h2>
                <p class="dk-level-counts uk-text-small">
% for label, count in card['counts']:
                    <span>${count} ${label}</span>
% endfor
                </p>
                <p class="uk-margin-remove-bottom">
                    <a class="uk-button uk-button-primary uk-button-small" href="${card['href']}">${L['study_path']}</a>
                    <a class="uk-button uk-button-default uk-button-small" href="${card['practice']}">${L['practise_level'].replace('{level}', card['level'])}</a>
                </p>
            </div>
        </li>
% endfor
    </ul>
</div>
