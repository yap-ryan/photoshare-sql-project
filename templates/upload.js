$(document).ready(function() {
    var $createalbum = $("#column_select"),
      $albumname = $("#layout_select");
  
    $city.hide();
  
    $createalbum.on('change', function() {
      if ($(this).val() == "col0") {
        $albumname.hide();
      } else {
        $albumname.show();
      }
    });
  
  })