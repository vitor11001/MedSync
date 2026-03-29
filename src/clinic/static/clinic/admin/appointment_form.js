document.addEventListener("DOMContentLoaded", () => {
  const amountInput = document.getElementById("id_amount_paid");

  if (!amountInput) {
    return;
  }

  const formatAmount = (value) => {
    const digits = value.replace(/\D/g, "").slice(0, 11);

    if (!digits.length) {
      return "";
    }

    const cents = digits.padStart(3, "0");
    const integerPart = cents.slice(0, -2).replace(/^0+(?=\d)/, "");
    const decimalPart = cents.slice(-2);

    return `${integerPart || "0"},${decimalPart}`;
  };

  amountInput.addEventListener("beforeinput", (event) => {
    if (
      event.data &&
      /\D/.test(event.data) &&
      event.inputType !== "deleteContentBackward" &&
      event.inputType !== "deleteContentForward"
    ) {
      event.preventDefault();
    }
  });

  amountInput.addEventListener("paste", (event) => {
    event.preventDefault();

    const pastedText = (event.clipboardData || window.clipboardData).getData("text");
    amountInput.value = formatAmount(pastedText);
  });

  amountInput.addEventListener("input", (event) => {
    event.target.value = formatAmount(event.target.value);
  });

  amountInput.value = formatAmount(amountInput.value);
});
