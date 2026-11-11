<!DOCTYPE html>
<html lang="${var['lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${var['page']['title']} | ${var['repo']['title']}</title>
    <link rel="icon" href="resources/themes/${var['theme']['id']}/images/logo.svg">
    <link rel="stylesheet" href="resources/vendor/uikit/css/uikit.min.css">
    <link rel="stylesheet" href="resources/themes/${var['theme']['id']}/framework/deutschkurs/deutschkurs.css">
    <script src="resources/vendor/uikit/js/uikit.min.js"></script>
    <script src="resources/vendor/uikit/js/uikit-icons.min.js"></script>
<%
    dk = var.get('dk')
    cfg = dk['settings'] if dk else None
    L = dk['labels'] if dk else None
    life = (('situations', 'situations.html'), ('conversations', 'conversations.html'), ('texts', 'texts.html'),
            ('photos', 'photos.html'), ('mistakes', 'mistakes.html'), ('inbox', 'inbox.html'))
    course = (('vocabulary', 'vocabulary.html'), ('verbs', 'verbs.html'), ('chunks', 'chunks.html'),
              ('grammar', 'grammar.html'))
%>
% if cfg:
    <style>:root { --dk-accent: ${cfg.accent}; --dk-m: ${cfg.gender_colors.get('m', '#1f6feb')}; --dk-f: ${cfg.gender_colors.get('f', '#cf222e')}; --dk-n: ${cfg.gender_colors.get('n', '#1a7f37')}; --dk-pl: ${cfg.gender_colors.get('pl', '#d4760a')}; }</style>
% endif
</head>
% if cfg:
<body data-speech="${'true' if cfg.speech else 'false'}" data-speech-lang="${cfg.speech_lang}" data-voice="${cfg.voice or ''}">
% else:
<body>
% endif
<div class="dk-page uk-background-muted">
<header class="dk-top" data-uk-sticky="show-on-up: true">
<div class="uk-container uk-container-small">
    <nav class="dk-bar uk-navbar-container uk-border-rounded uk-box-shadow-medium" data-uk-navbar>
        <div class="uk-navbar-left">
            <a class="dk-brand uk-navbar-item uk-logo" href="index.html" title="${var['repo']['title']}"><img src="resources/themes/${var['theme']['id']}/images/logo.svg" width="24" height="24" alt="${var['repo']['title']}"></a>
% if dk:
            <ul class="dk-nav uk-navbar-nav uk-visible@m">
                <li><a href="index.html">${L['home']}</a></li>
                <li>
                    <a href="#">${L['menu_life']} <span data-uk-navbar-parent-icon></span></a>
                    <div class="uk-navbar-dropdown">
                        <ul class="uk-nav uk-navbar-dropdown-nav">
% for key, href in life:
                            <li><a href="${href}">${L[key]}</a></li>
% endfor
                        </ul>
                    </div>
                </li>
                <li>
                    <a href="#">${L['menu_course']} <span data-uk-navbar-parent-icon></span></a>
                    <div class="uk-navbar-dropdown">
                        <ul class="uk-nav uk-navbar-dropdown-nav">
% for key, href in course:
                            <li><a href="${href}">${L[key]}</a></li>
% endfor
                        </ul>
                    </div>
                </li>
                <li><a href="skill.html">${L['skill']}</a></li>
            </ul>
% endif
        </div>
        <div class="uk-navbar-right">
% if var.get('search_box'):
            <a class="uk-navbar-toggle" href="#dk-search" data-uk-toggle title="${L['search'] if L else 'Search'}" aria-label="${L['search'] if L else 'Search'}"><span data-uk-icon="search"></span></a>
% endif
% if dk:
            <a class="uk-navbar-toggle uk-hidden@m" href="#dk-menu" data-uk-toggle title="${L['menu']}" aria-label="${L['menu']}"><span data-uk-navbar-toggle-icon></span></a>
% endif
        </div>
    </nav>
</div>
</header>
% if dk:
<div id="dk-menu" data-uk-offcanvas="flip: true; overlay: true">
    <div class="uk-offcanvas-bar">
        <button class="uk-offcanvas-close" type="button" data-uk-close aria-label="Close"></button>
        <ul class="uk-nav uk-nav-default">
            <li><a href="index.html">${L['home']}</a></li>
            <li class="uk-nav-header">${L['menu_life']}</li>
% for key, href in life:
            <li><a href="${href}">${L[key]}</a></li>
% endfor
            <li class="uk-nav-header">${L['menu_course']}</li>
% for key, href in course:
            <li><a href="${href}">${L[key]}</a></li>
% endfor
            <li class="uk-nav-divider"></li>
            <li><a href="skill.html">${L['skill']}</a></li>
        </ul>
    </div>
</div>
% endif
% if var.get('search_box'):
<div id="dk-search" data-uk-modal>
    <div class="uk-modal-dialog uk-modal-body">
        ${var['search_box'] | n}
    </div>
</div>
% endif
