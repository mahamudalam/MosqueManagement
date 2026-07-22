$(document).ready(function () {
    $('#member').select2({
        placeholder: "Search Member",
        allowClear: true,
        width: '100%'
    });
});


function populateFridays() {

    const month = document.getElementById("month");
    const friday = document.getElementById("friday_date");

    if (!month || !friday) return;

    friday.innerHTML = '<option value="">Select Friday</option>';

    if (!month.value) return;

    const [year, mon] = month.value.split("-");

    let date = new Date(year, mon - 1, 1);

    while (date.getMonth() == mon - 1) {

        if (date.getDay() === 5) {

            const option = document.createElement("option");

            const yyyy = date.getFullYear();
            const mm = String(date.getMonth() + 1).padStart(2, '0');
            const dd = String(date.getDate()).padStart(2, '0');

            option.value = `${yyyy}-${mm}-${dd}`;

            option.text = date.toLocaleDateString("en-GB", {
                day: "2-digit",
                month: "short",
                year: "numeric"
            });

            friday.appendChild(option);
        }

        date.setDate(date.getDate() + 1);
    }
}

$(document).ready(function () {

    if ($("#member").length) {
        $("#member").select2({
            placeholder: "Search Member",
            allowClear: true,
            width: "100%"
        });
    }

    populateFridays();

    $("#month").on("change", populateFridays);

});