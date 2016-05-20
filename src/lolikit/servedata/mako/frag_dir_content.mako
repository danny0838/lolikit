<div class="lolinote-dir-content">
  <p class="sr-only">directories list:</p>
  <div class="list-group">
    % for name, baseon_rootdir, dirmark in dir_content_data['array']:
      <%
        if dirmark:
          a_color_class = 'list-group-item-warning'
          icon = '<span class="glyphicon glyphicon-folder-close"></span>'
        elif name.endswith('.md'):
          a_color_class = ''
          icon = '<span class="glyphicon glyphicon-file"></span>'
        else:
          a_color_class = 'disabled'
          icon = '<span class="glyphicon glyphicon-file"></span>'
      %>
      <a href="${dir_content_data['prepend_url']}${baseon_rootdir}${dirmark}" class="list-group-item ${a_color_class}">
        <span class="sr-only"><b>${'{:\u00A0>2}'.format(loop.index + 1)}. </b></span>
        ${icon}
        ${name}${dirmark}
        <span class="sr-only"><br/></span>
      </a>
    % endfor
  </div>
</div>
