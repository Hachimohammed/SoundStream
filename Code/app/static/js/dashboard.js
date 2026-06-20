var now = new Date();

var day = ("0" + now.getDate()).slice(-2);   
var month = ("0" + (now.getMonth() + 1)).slice(-2); 
var today = now.getFullYear() + "-" + month + "-" + day;

document.getElementById("date_event").setAttribute("min", today);

/** Replacement of choose file by file name */
document.getElementById('file').addEventListener('change', function(e) {
        const label = document.querySelector('label[for="file"]');
        const fileName = e.target.files[0]?.name || 'Choose file';
        label.textContent = fileName;
});