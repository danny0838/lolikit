<!DOCTYPE HTML>
<html>
  <head>
    <meta charset="UTF-8" />

    <title>${ base_data['page_title'] }</title>
    <meta name="description" content="${ base_data['description'] }">
    <meta property="og:title" content="${ base_data['page_title'] }">
    <meta property="og:description" content="${ base_data['description'] }">
    <meta name="og:title" content="${ base_data['page_title'] }">
    <meta name="og:description" content="${ base_data['description'] }">

    <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/lolinote/lolinote.css">
    <script src="/static/jquery/jquery-2.2.3.min.js"></script>
    <script src="/static/bootstrap/js/bootstrap.min.js"></script>

    <meta name="viewport" content="width=device-width, initial-scale=1">
  </head>
  <body>
    <div class="container">
      <%include file="frag_navbar.mako" />
      <%block name="content" />
    </div>
  </body>
</html>
