function updateDateTime() {
    const now = new Date();

    const date = now.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });

    const time = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });

    const element = document.getElementById("currentDateTime");
    if (element) {
        element.innerHTML = `📅 ${date} &nbsp;|&nbsp; 🕒 ${time}`;
    }
}

updateDateTime();

// Update every minute
setInterval(updateDateTime, 30000);