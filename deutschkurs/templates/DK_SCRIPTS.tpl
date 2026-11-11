<%
    js = 'resources/themes/' + var['theme']['id'] + '/framework/deutschkurs/'
%>
<script type="application/json" id="dk-practice-labels">${var['labels_json'] | n}</script>
<script src="deutschkurs-data.js"></script>
<script src="${js}answer.js"></script>
<script src="${js}scheduler.js"></script>
<script src="${js}practice-core.js"></script>
<script src="${js}store.js"></script>
% for name in var.get('extra', ()):
<script src="${js}${name}"></script>
% endfor
