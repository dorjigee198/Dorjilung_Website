(function () {
  var form = document.getElementById("grievance-form");
  if (!form) return;

  var MAX_BYTES = 50 * 1024 * 1024;

  var anonInput = form.querySelector(".dhpl-switch-input");
  var identityFields = document.getElementById("grievance-identity-fields");
  var requiredNames = ["full_name", "cid_number", "phone"];

  function applyAnonymousState() {
    var isAnonymous = anonInput.checked;
    if (identityFields) {
      identityFields.classList.toggle("is-anonymous", isAnonymous);
    }
    requiredNames.forEach(function (name) {
      var field = form.querySelector('[name="' + name + '"]');
      if (field) field.required = !isAnonymous;
    });
  }

  if (anonInput) {
    anonInput.addEventListener("change", applyAnonymousState);
    applyAnonymousState();
  }

  function wireFileInput(inputName, labelId, defaultText) {
    var input = form.querySelector('[name="' + inputName + '"]');
    var label = document.getElementById(labelId);
    var errorBox = document.getElementById("grievance-upload-error");
    if (!input) return;

    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) {
        if (label) label.textContent = defaultText;
        return;
      }
      if (file.size > MAX_BYTES) {
        if (errorBox) errorBox.textContent = file.name + " is too large — the limit is 50MB.";
        input.value = "";
        if (label) label.textContent = defaultText;
        return;
      }
      if (errorBox) errorBox.textContent = "";
      if (label) label.textContent = file.name;
    });
  }

  wireFileInput("audio_file", "grievance-audio-filename", "Upload a voice recording");
  wireFileInput("video_file", "grievance-video-filename", "Browse files");
})();
