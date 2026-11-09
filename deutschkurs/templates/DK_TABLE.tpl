<%
    L = var['dk']['labels']
%>
<div class="dk-list dk-no-link">
% if var['rows']:
    <p class="dk-filter-bar">
        <input type="search" class="dk-filter" data-table="dk-table" placeholder="${L['filter_placeholder']}" aria-label="${L['filter']}">
% for column in var['filters']:
        <select class="dk-filter-select" data-table="dk-table" data-column="${column}" aria-label="${var['columns'][column]}">
            <option value="">${var['columns'][column]}: ${L['all']}</option>
% for value in sorted({row[column]['text'] for row in var['rows'] if row[column]['text']}):
            <option value="${value}">${value}</option>
% endfor
        </select>
% endfor
    </p>
    <table id="dk-table" class="dk-table">
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
% endif
</div>
