<!DOCTYPE html>
<html lang="${var['lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${var['page']['title']} | ${var['repo']['title']}</title>
    <link rel="icon" href="resources/themes/${var['theme']['id']}/images/logo.svg">
    <link rel="stylesheet" href="resources/themes/${var['theme']['id']}/framework/deutschkurs/deutschkurs.css">
<%
    dk = var.get('dk')
    cfg = dk['settings'] if dk else None
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
<header class="dk-top">
    <a class="dk-brand" href="index.html">${var['repo']['title']}</a>
    <nav class="dk-nav">
% if dk:
        <a href="index.html">${dk['labels']['home']}</a>
        <a href="vocabulary.html">${dk['labels']['vocabulary']}</a>
        <a href="verbs.html">${dk['labels']['verbs']}</a>
        <a href="chunks.html">${dk['labels']['chunks']}</a>
        <a href="grammar.html">${dk['labels']['grammar']}</a>
% endif
    </nav>
    ${var['search_box'] | n}
</header>
