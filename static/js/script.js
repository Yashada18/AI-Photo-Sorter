document.addEventListener("DOMContentLoaded", () => {
    const uploadBtn = document.getElementById("uploadBtn");
    const imageUpload = document.getElementById("imageUpload");
    const previewContainer = document.getElementById("previewContainer");

    // Open file input when upload button is clicked
    uploadBtn.addEventListener("click", () => {
        imageUpload.click(); // Trigger file input when upload button is clicked
    });

    // Handle file selection and preview
    imageUpload.addEventListener("change", (event) => {
        previewContainer.innerHTML = ""; // Clear previous previews
        const files = event.target.files;

        if (files.length === 0) return;

        // Display selected images as preview
        for (const file of files) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = document.createElement("img");
                img.src = e.target.result;
                img.style.maxWidth = "100px"; // Optional: to scale down images in preview
                img.style.margin = "10px";
                previewContainer.appendChild(img);
            };
            reader.readAsDataURL(file);
        }

        // Now upload the selected files
        const formData = new FormData();
        for (const file of files) {
            formData.append("images", file); // Append each file to the FormData
        }

        // Upload the images via fetch API
        fetch("/upload", {
            method: "POST",
            body: formData, // Send the form data with files
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message); // Show success message
                } else if (data.error) {
                    alert(data.error); // Show error message
                }
            })
            .catch(error => {
                console.error("Error uploading files:", error);
                alert("Something went wrong during the upload.");
            });
    });
});
