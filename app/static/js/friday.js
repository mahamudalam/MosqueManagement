document.addEventListener("DOMContentLoaded", function () {

    const contributionMode = document.getElementById("contribution_mode");
    const amountInput = document.getElementById("amount");
    const memberSelect = document.getElementById("member");

    if (!contributionMode || !amountInput || !memberSelect) {
        return;
    }

    function toggleAmountField() {

        const selectedMember =
            memberSelect.options[memberSelect.selectedIndex].text.trim().toLowerCase();

        // If Rice is selected and member is NOT Admin
        if (contributionMode.value === "Rice" && selectedMember !== "masjid khajanchi") {
            amountInput.value = 0;
            amountInput.readOnly = true;
            amountInput.style.backgroundColor = "#e9ecef";
        } else {
            amountInput.readOnly = false;
            amountInput.style.backgroundColor = "";

            // Clear only if switching back from Rice
            if (amountInput.value == 0) {
                amountInput.value = "";
            }
        }
    }

    // Initial page load
    toggleAmountField();

    // When member changes
    memberSelect.addEventListener("change", toggleAmountField);

    // When contribution mode changes
    contributionMode.addEventListener("change", toggleAmountField);

});

$(document).ready(function () {

    $('#friday_date').select2({
        placeholder: "Select Friday(s)",
        allowClear: true,
        closeOnSelect: false,
        width: '100%'
    });

});
