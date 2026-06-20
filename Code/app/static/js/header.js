/* Header Clock Script */
function updateClock() {
    const now = new Date();
    const dateOptions = { day: 'numeric', month: 'long', year: 'numeric' };
    const dateString = now.toLocaleDateString('en-GB', dateOptions);
    const timeString = now.toLocaleTimeString('fr-FR'); 
    const clockElement = document.getElementById('clock');
    if (clockElement) {
        clockElement.innerText = `${dateString} - ${timeString}`;
    }
}
updateClock();

setInterval(updateClock, 1000);
