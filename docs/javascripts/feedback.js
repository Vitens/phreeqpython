(function () {
  function bindFeedback() {
    var feedback = document.forms.feedback;
    if (!feedback) {
      return;
    }

    feedback.hidden = false;
    if (feedback.dataset.bound === "true") {
      return;
    }
    feedback.dataset.bound = "true";

    feedback.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var data = ev.submitter && ev.submitter.getAttribute("data-md-value");
      feedback.firstElementChild.disabled = true;
      var note = feedback.querySelector(
        ".md-feedback__note [data-md-value='" + data + "']",
      );
      if (note) {
        note.hidden = false;
      }
    });
  }

  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(bindFeedback);
  } else {
    document.addEventListener("DOMContentLoaded", bindFeedback);
  }
})();
