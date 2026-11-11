<%
    L = var['dk']['labels']
%>
<div class="dk-practice dk-no-link">
    <noscript><p class="uk-alert uk-alert-warning">${L['needs_js']}</p></noscript>
    <p id="dk-storage-off" class="uk-alert uk-alert-warning" hidden>${L['storage_off']}</p>
    <p id="dk-no-data" class="uk-alert uk-alert-danger" hidden>${L['no_data']}</p>
    <div id="dk-sessions" class="uk-grid-small uk-child-width-1-2@s" data-uk-grid>
% for kind in ('daily', 'short', 'weekly'):
        <div>
            <div class="uk-card uk-card-default uk-card-small uk-card-body uk-border-rounded">
                <button type="button" class="dk-session uk-button uk-button-primary" data-session="${kind}">${L[kind]}</button>
                <p class="uk-text-small uk-margin-small-top">${L['session_' + kind]}</p>
            </div>
        </div>
% endfor
        <div>
            <div class="uk-card uk-card-default uk-card-small uk-card-body uk-border-rounded">
                <button type="button" class="dk-session uk-button uk-button-default" data-session="free">${L['free']}</button>
                <p class="uk-text-small uk-margin-small-top">${L['session_free']}</p>
                <div class="dk-free-filters uk-flex uk-flex-wrap">
% for key, label, values in var['filters']:
                    <select class="uk-select uk-form-small uk-form-width-small" data-filter="${key}" aria-label="${label}">
                        <option value="">${label}: ${L['all']}</option>
% for value, text in values:
                        <option value="${value}">${text}</option>
% endfor
                    </select>
% endfor
                </div>
            </div>
        </div>
    </div>
    <div id="dk-practice-card" class="dk-practice-card uk-card uk-card-default uk-card-body uk-border-rounded uk-margin" hidden aria-live="polite"></div>
    <p class="dk-progress-tools uk-margin-top">
        <button type="button" id="dk-export" class="uk-button uk-button-default uk-button-small">${L['export']}</button>
        <label class="uk-button uk-button-default uk-button-small" for="dk-import">${L['import']}</label>
        <input type="file" id="dk-import" accept="application/json,.json" hidden>
        <span id="dk-import-result" class="uk-text-small"></span>
    </p>
    ${var['scripts'] | n}
</div>
