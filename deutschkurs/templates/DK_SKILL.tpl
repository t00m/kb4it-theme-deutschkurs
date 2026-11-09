<div class="dk-skill dk-no-link">
    <section class="dk-card">
        <p>This course comes with a skill: instructions an AI assistant follows to help you add entries from real material, correct your German and fix build problems. It removes personal data before anything else.</p>
        <ul>
            <li>Claude Code: copy the folder <code>skills/deutschkurs/</code> of this site to <code>~/.claude/skills/deutschkurs/</code>.</li>
            <li>Another assistant: give it <a href="${var['skill_url']}">SKILL.md</a> and the files in <code>reference/</code> as instructions.</li>
            <li><a href="${var['site_url']}">reference/site.md</a> lists the entries of this course, so the assistant reuses their names.</li>
        </ul>
    </section>
    ${var['skill_html'] | n}
</div>
