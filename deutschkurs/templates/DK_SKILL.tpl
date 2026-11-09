<%
    L = var['dk']['labels']
%>
<div class="dk-skill dk-no-link">
    <section class="dk-card">
        <p>${L['skill_intro']}</p>
        <ul>
            <li>${L['skill_claude']}</li>
            <li>${L['skill_other']} <a href="${var['skill_url']}">SKILL.md</a></li>
            <li>${L['skill_site']} <a href="${var['site_url']}">reference/site.md</a></li>
        </ul>
    </section>
    ${var['skill_html'] | n}
</div>
