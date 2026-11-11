<!-- Add page on UIkit, as in techdoc: one card per entry type. -->
<div class="kb-add">
    <div class="kb-add-note uk-alert uk-alert-primary">
        <strong>Note:</strong> This page saves or downloads the Markdown file for you.
        Click <em>Create</em> on any card, edit the template, then <em>Save</em> it
        (or <em>Copy</em> the text). Put the file in your repository's <strong>source</strong>
        folder and rebuild.
    </div>
    <div class="uk-grid-small uk-child-width-1-2@s uk-child-width-1-3@m" data-uk-grid>
% for cat in var['page']['categories']:
        <div>
            <div class="uk-card uk-card-default uk-card-hover uk-card-small kb-add-card" style="border-top: 3px solid ${cat['color']};">
                <div class="uk-card-header kb-add-card-header">
                    <h3 class="uk-card-title uk-margin-remove kb-add-card-title" style="color: ${cat['color']};">Add ${cat['name']}</h3>
                </div>
                <div class="uk-card-body kb-add-card-body">
                    <p class="uk-margin-remove">${cat['description']}</p>
                </div>
                <div class="uk-card-footer kb-add-card-footer">
                    <button class="uk-button uk-button-small uk-button-primary" type="button" data-kb-open="${cat['id']}">Create</button>
                </div>
            </div>
        </div>
% endfor
    </div>
</div>

${var['page']['editor_dialogs'] | n}
