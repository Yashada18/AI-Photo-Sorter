document.getElementById('uploadBtn').addEventListener('click', function() {
    document.getElementById('imageUpload').click(); // Open file selector
});

document.getElementById('imageUpload').addEventListener('change', function(event) {
    let files = event.target.files;
    let previewContainer = document.getElementById('previewContainer');
    previewContainer.innerHTML = ''; // Clear previous images

    for (let file of files) {
        let reader = new FileReader();
        reader.onload = function(e) {
            let img = document.createElement('img');
            img.src = e.target.result;
            img.classList.add('preview-image'); // Add class for styling
            previewContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
});
