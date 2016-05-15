<nav class="navbar navbar-default">
  <div class="container-fluid">
    <div class="navbar-header">
      <button
        type="button"
        class="navbar-toggle collapsed"
        data-toggle="collapse"
        data-target="#loli-navbar-collapse"
        aria-expanded="false">
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <span class="navbar-brand">
        <strong>
          ${ base_data['item_title'] }
        </strong>
        <span class="sr-only">(${base_data['current_mode']} mode)</span>
      </span>
    </div>
    <div class="collapse navbar-collapse" id="loli-navbar-collapse">
      <h3 class="sr-only">Mode Selection:</h3>
      <ol class="nav navbar-nav navbar-right">
        <li class="${'active' if base_data['current_mode'] == 'source' else ''}">
          <a href="/source/${base_data['rel_filepath']}${base_data['dirmark']}">source</a>
        </li>
        <li class="${'active' if base_data['current_mode'] == 'note' else ''}">
          <a href="/note/${base_data['rel_filepath']}${base_data['dirmark']}">note</a>
        </li>
      </ol>
    </div>
  </div>
</nav>
