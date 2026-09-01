(function () {
  var form = document.querySelector(".dhpl-tender-search");
  if (!form) return;

  var sortSelect = form.querySelector('select[name="sort"]');
  var groupToggle = form.querySelector('input[name="group"]');

  if (sortSelect) {
    sortSelect.addEventListener("change", function () {
      form.submit();
    });
  }
  if (groupToggle) {
    groupToggle.addEventListener("change", function () {
      form.submit();
    });
  }
})();
