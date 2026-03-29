(function ($) {
  $(function () {
    const $inputs = $("#id_doctor_percentage, #id_clinic_percentage");

    if (!$inputs.length || typeof $.fn.mask !== "function") {
      return;
    }

    $inputs.mask("##0,00%", {
      reverse: true,
    });
  });
})(window.jQuery);
