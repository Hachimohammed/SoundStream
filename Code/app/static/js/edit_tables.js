document.getElementById('file').addEventListener('change', function(e) {
        const label = document.querySelector('label[for="file"]');
        const fileName = e.target.files[0]?.name || 'Choose file';
        label.textContent = fileName;
});