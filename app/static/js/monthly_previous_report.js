document.addEventListener("DOMContentLoaded", function () {

    const year = document.getElementById("reportYear");
    const month = document.getElementById("reportMonth");

    function loadReport() {

        if (!year.value || !month.value) {
            return;
        }

        document.getElementById("monthlyReportCard").innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border text-primary"></div>
                <p class="mt-2">Loading report...</p>
            </div>
        `;

        fetch(`/reports/monthly-report?year=${year.value}&month=${month.value}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById("monthlyReportCard").innerHTML = html;
            })
            .catch(error => {
                console.error(error);
            });

    }

    year.addEventListener("change", loadReport);
    month.addEventListener("change", loadReport);

});