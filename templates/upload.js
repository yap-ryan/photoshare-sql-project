$(document).ready(function() {
    var $createalbum = $("#createalbum"),
      $albumname = $("#albumname");
  
    $albumname.hide();
  
    $createalbum.on('change', function() {
      if (($(this).val() == "col0") || ($(this).val() == "col2")) {
        $albumname.hide();
      } else {
        $albumname.show();
      }
    });
  
  })

