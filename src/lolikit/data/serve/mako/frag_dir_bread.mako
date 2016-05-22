<div class="row nav">
  <div class="col-md-12">
    <h3 class="sr-only">Breadcrumb:</h3>
    <ol class="breadcrumb">
      % for name, baseon_rootdir, dirmark in dir_bread_data['array']:
        <li>
          <span class="glyphicon glyphicon-folder-close"></span>
          <a href="${dir_bread_data['prepend_url']}${baseon_rootdir}${dirmark}">${name}</a>
        </li>
      % endfor
    </ol>
  </div>
</div>
