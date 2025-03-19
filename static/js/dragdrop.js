document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"]');
    const uploadButton = document.getElementById('uploadButton');
    const fileError = document.getElementById('fileError');
    const allowedTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'heif', 'pdf'];

    //Validating dropped file
    function validateFile(file) {
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExtension)) {
            uploadButton.disabled = true;
            fileError.style.display = 'block';
            fileInput.value = ''; // Clear the file input
            return false;
        }
        uploadButton.disabled = false;
        fileError.style.display = 'none';
        return true;
    }

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Changing the Opacity for better visual
    ['dragenter', 'dragover'].forEach(eventName => {
        document.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        document.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        document.body.style.opacity = '0.7';
        document.body.style.transition = 'opacity 0.2s ease';
    }

    function unhighlight(e) {
        document.body.style.opacity = '1';
    }

    // Update file name display function
    function updateFileNameDisplay() {
        const selectedFiles = document.getElementById('selectedFiles');
        if (selectedFiles) {
            if (fileInput.files.length > 0) {
                if (fileInput.files.length === 1) {
                    selectedFiles.textContent = fileInput.files[0].name;
                } else {
                    selectedFiles.textContent = fileInput.files.length + ' files selected';
                }
            } else {
                selectedFiles.textContent = 'No file chosen';
            }
        }
    }

    document.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            const file = files[0];
            if (validateFile(file)) {
                // Update the file input with the dropped file
                fileInput.files = files;
                
                // Update the file name display
                updateFileNameDisplay();
                
                // Show upload form if hidden
                const uploadForm = document.getElementById('uploadForm');
                if (uploadForm.style.display === 'none' || uploadForm.style.display === '') {
                    uploadForm.style.display = 'block';
                }
            }
        }
    });
});