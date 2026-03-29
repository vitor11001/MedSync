(function ($) {
  const initializeAmountMask = () => {
    const $amountInput = $("#id_amount_paid");

    if (!$amountInput.length || typeof $.fn.mask !== "function") {
      return;
    }

    if ($amountInput.data("mask-initialized")) {
      return;
    }

    $amountInput.mask("#########0,00", {
      reverse: true,
    });
    $amountInput.data("mask-initialized", true);
  };

  initializeAmountMask();
  $(initializeAmountMask);
  document.addEventListener("DOMContentLoaded", initializeAmountMask);
  window.addEventListener("load", initializeAmountMask);
})(window.jQuery);
