<%
    L = var['dk']['labels']
    tid = var.get('table_id') or 'dk-table'
%>
<div class="dk-list dk-no-link">
% if var.get('intro'):
    ${var['intro'] | n}
% endif
% if var['rows']:
    <div class="dk-filter-bar uk-flex uk-flex-wrap uk-margin">
        <input type="search" class="dk-filter uk-input uk-form-small uk-form-width-medium" data-table="${tid}" placeholder="${L['filter_placeholder']}" aria-label="${L['filter']}">
% for column in var['filters']:
        <select class="dk-filter-select uk-select uk-form-small uk-form-width-small" data-table="${tid}" data-column="${column}" aria-label="${var['columns'][column]}">
            <option value="">${var['columns'][column]}: ${L['all']}</option>
% for value in sorted({row[column]['text'] for row in var['rows'] if row[column]['text']}):
            <option value="${value}">${value}</option>
% endfor
        </select>
% endfor
    </div>
    <div class="uk-overflow-auto">
    <table id="${tid}" class="dk-table uk-table uk-table-divider uk-table-small uk-table-hover">
        <thead><tr>
% for column in var['columns']:
            <th>${column}</th>
% endfor
        </tr></thead>
        <tbody>
% for row in var['rows']:
            <tr class="dk-row">
% for c in row:
% if c['href']:
                <td><a class="${c['css']}" href="${c['href']}" lang="de">${c['text']}</a></td>
% elif c['css']:
                <td class="${c['css']}">${c['text']}</td>
% else:
                <td>${c['text']}</td>
% endif
% endfor
            </tr>
% endfor
        </tbody>
    </table>
    </div>
% endif
</div>
