<%
    dk = var.get('dk')
    js = 'resources/themes/' + var['theme']['id'] + '/framework/deutschkurs/'
%>
% if dk:
<p class="dk-voice-note uk-container uk-container-small uk-text-small uk-text-muted">${dk['labels']['no_voice']}</p>
% endif
<footer class="dk-footer uk-container uk-container-small uk-text-small uk-text-muted">${dk['labels']['built_with'] if dk else 'Built with KB4IT on'} ${var['updated']}</footer>
</div>
<script src="${js}core.js"></script>
<script src="${js}speech.js"></script>
<script src="${js}ui.js"></script>
</body>
</html>
