<%inherit file="base.mako"/>
<%block name="content">
  <%include file="frag_dir_bread.mako" />

  <div class="panel panel-default">
    <div class="panel-heading sr-only">
      <h3>Content:</h3>
    </div>
    <div class="panel-body">
      % if note_data['render']:
        <div class="lolinote-content">
          ${note_data['content']}
        </div>
      % else:
        <pre class="lolinote-content">${note_data['content']}</pre>
      % endif
    </div>
  </div>
</%block>
