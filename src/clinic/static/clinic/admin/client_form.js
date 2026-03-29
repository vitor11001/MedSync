(function ($) {
  $(function () {
    if (typeof $.fn.mask !== "function") {
      return;
    }

    const $cpfInput = $("#id_cpf");
    const $birthDateInput = $("#id_birth_date");
    const $phoneInputs = $("#id_phone_primary, #id_phone_secondary");

    if ($cpfInput.length) {
      $cpfInput.mask("000.000.000-00");
    }

    if ($birthDateInput.length) {
      $birthDateInput.mask("00/00/0000");
    }

    if ($phoneInputs.length) {
      $phoneInputs.mask("(00) 00000-0000");
    }
  });
})(window.jQuery);
