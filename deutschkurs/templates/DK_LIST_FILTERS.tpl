<%
    L = var['dk']['labels']
%>
% if var['filters']:
    <div class="dk-list-filters" hidden>
        <div class="uk-flex uk-flex-wrap uk-margin">
% for key, label, values in var['filters']:
        <label>${label}
            <select class="dk-list-filter uk-select uk-form-small" data-key="${key}">
                <option value="">${L['all']}</option>
% for value in values:
                <option value="${value}">${value}</option>
% endfor
            </select>
        </label>
% endfor
        </div>
    </div>
% endif
