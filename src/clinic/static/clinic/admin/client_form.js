document.addEventListener("DOMContentLoaded", () => {
  const cpfInput = document.getElementById("id_cpf");
  const birthDateInput = document.getElementById("id_birth_date");
  const phoneInputs = [
    document.getElementById("id_phone_primary"),
    document.getElementById("id_phone_secondary"),
  ].filter(Boolean);

  const formatCpf = (value) => {
    const digits = value.replace(/\D/g, "").slice(0, 11);
    const parts = [];

    if (digits.length > 0) {
      parts.push(digits.slice(0, 3));
    }

    if (digits.length > 3) {
      parts.push(digits.slice(3, 6));
    }

    if (digits.length > 6) {
      parts.push(digits.slice(6, 9));
    }

    let formatted = parts.join(".");

    if (digits.length > 9) {
      formatted += `-${digits.slice(9, 11)}`;
    }

    return formatted;
  };

  const formatDate = (value) => {
    const digits = value.replace(/\D/g, "").slice(0, 8);
    let formatted = "";

    if (digits.length > 0) {
      formatted = digits.slice(0, 2);
    }

    if (digits.length > 2) {
      formatted += `/${digits.slice(2, 4)}`;
    }

    if (digits.length > 4) {
      formatted += `/${digits.slice(4, 8)}`;
    }

    return formatted;
  };

  const formatPhone = (value) => {
    const digits = value.replace(/\D/g, "").slice(0, 11);

    if (digits.length <= 2) {
      return digits.length ? `(${digits}` : "";
    }

    if (digits.length <= 7) {
      return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
    }

    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
  };

  if (cpfInput) {
    cpfInput.addEventListener("input", (event) => {
      event.target.value = formatCpf(event.target.value);
    });

    cpfInput.value = formatCpf(cpfInput.value);
  }

  if (birthDateInput) {
    birthDateInput.addEventListener("input", (event) => {
      event.target.value = formatDate(event.target.value);
    });

    birthDateInput.value = formatDate(birthDateInput.value);
  }

  phoneInputs.forEach((input) => {
    input.setAttribute("maxlength", "15");

    input.addEventListener("input", (event) => {
      event.target.value = formatPhone(event.target.value);
    });

    input.addEventListener("beforeinput", (event) => {
      if (
        event.data &&
        /\D/.test(event.data) &&
        event.inputType !== "deleteContentBackward" &&
        event.inputType !== "deleteContentForward"
      ) {
        event.preventDefault();
      }
    });

    input.addEventListener("paste", (event) => {
      event.preventDefault();

      const pastedText = (event.clipboardData || window.clipboardData).getData("text");
      const digits = pastedText.replace(/\D/g, "").slice(0, 11);
      input.value = formatPhone(digits);
    });

    input.value = formatPhone(input.value);
  });
});
