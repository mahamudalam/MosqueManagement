
document.addEventListener("DOMContentLoaded", function () {

    const memberField = document.getElementById("member");
    const amountField = document.getElementById("amount");

    if (!memberField || !amountField) {
        console.error("Member or Amount field not found.");
        return;
    }

    console.log("Imam Salary Contribution JS loaded.");

    memberField.addEventListener("change", async function () {

        const memberId = this.value;

        console.log("Selected Member ID:", memberId);

        // Clear amount when member changes
        amountField.value = "";

        if (!memberId) {
            return;
        }

        // Generate API URL using selected member ID
        const baseUrl = memberField.dataset.apiUrl;
        const apiUrl = baseUrl.replace(/\/0\/?$/, "/" + memberId);

        console.log("Calling API:", apiUrl);

        try {
            const response = await fetch(apiUrl);

            if (!response.ok) {
                throw new Error("API request failed: " + response.status);
            }

            const data = await response.json();

            console.log("API Response:", data);

            if (data.success) {
                amountField.value = data.amount;
                console.log("Amount successfully populated:", data.amount);
            } else {
                alert(data.message || "Unable to fetch contribution amount.");
            }

        } catch (error) {
            console.error("Error fetching contribution amount:", error);
            alert("Unable to fetch member contribution amount.");
        }
    });

});
