// template/posts/posts_base.html
function setImageSize() {
  var imgs = document.getElementsByClassName('imagePost');
  for (var i = 0; i < imgs.length; i++) {
    imgs[i].height = 0.8 * imgs[i].height;
    imgs[i].width = 0.8 * imgs[i].width;
  }
}

// template/posts/post_form.html
$(document).ready(function() {
  $(".fa-camera").hide();
  $("#id_image_file").hide();
  $('#id_content_type').on('change', function() {
    if (this.value == 'image/png;base64' || this.value == 'image/jpeg;base64') {
      $("#id_content").attr("required", false)
      $("#id_content").hide();
      $(".fa-camera").show();
      $("#id_image_file").show();
    } else {
      $(".fa-camera").hide();
      $("#id_image_file").hide();
      $("#id_content").show();
    }
  });
});