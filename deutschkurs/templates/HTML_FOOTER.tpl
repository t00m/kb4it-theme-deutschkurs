<%
    dk = var.get('dk')
    js = 'resources/themes/' + var['theme']['id'] + '/framework/deutschkurs/'
%>
% if dk:
<p class="dk-voice-note">${dk['labels']['no_voice']}</p>
% endif
<footer class="dk-footer">${dk['labels']['built_with'] if dk else 'Built with KB4IT on'} ${var['updated']}</footer>
<script src="${js}core.js"></script>
<script src="${js}speech.js"></script>
</body>
</html>
