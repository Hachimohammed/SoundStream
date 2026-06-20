document.getElementById('file').addEventListener('change', function(e) {
                        const fileName = e.target.files[0]?.name || 'No file chosen';
                        document.getElementById('file-name').textContent = fileName;
                        document.getElementById('filename-hidden').value = fileName;
                    });