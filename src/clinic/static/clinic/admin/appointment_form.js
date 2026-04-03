(function ($) {
  const initializeAmountMask = () => {
    const $amountInputs = $(".js-money-mask");

    if (!$amountInputs.length || typeof $.fn.mask !== "function") {
      return;
    }

    $amountInputs.each(function () {
      const $input = $(this);

      if ($input.data("mask-initialized")) {
        return;
      }

      $input.mask("#########0,00", {
        reverse: true,
      });
      $input.data("mask-initialized", true);
    });
  };

  initializeAmountMask();
  $(initializeAmountMask);
  document.addEventListener("DOMContentLoaded", initializeAmountMask);
  window.addEventListener("load", initializeAmountMask);
  document.addEventListener("formset:added", initializeAmountMask);
})(window.jQuery);
