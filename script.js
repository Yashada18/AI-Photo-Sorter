document.addEventListener("DOMContentLoaded", () => {
    const uploadBtn = document.getElementById("uploadBtn");
    const imageUpload = document.getElementById("imageUpload");
    const previewContainer = document.getElementById("previewContainer");

    // Open file input when upload button is clicked
    uploadBtn.addEventListener("click", () => {
        imageUpload.click();
    });

    // Handle file selection and preview
    imageUpload.addEventListener("change", (event) => {
        previewContainer.innerHTML = ""; // Clear previous previews
        const files = event.target.files;

        if (files.length === 0) return;

        for (const file of files) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement("img");
                img.src = e.target.result;
                previewContainer.appendChild(img);
            };
            reader.readAsDataURL(file);
        }
    });
});
