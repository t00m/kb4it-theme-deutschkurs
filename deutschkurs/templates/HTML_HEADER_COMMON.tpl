<!DOCTYPE html>
<html lang="${var['lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${var['page']['title']} | ${var['repo']['title']}</title>
    <link rel="icon" href="resources/themes/${var['theme']['id']}/images/logo.svg">
    <link rel="stylesheet" href="resources/themes/${var['theme']['id']}/framework/deutschkurs/deutschkurs.css">
</head>
<body>
<header class="dk-top">
    <a class="dk-brand" href="index.html">${var['repo']['title']}</a>
    <nav class="dk-nav"></nav>
    ${var['search_box'] | n}
</header>
