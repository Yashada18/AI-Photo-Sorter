document.addEventListener("DOMContentLoaded", () => {
    const folderBtn = document.getElementById("uploadFolderBtn");
    const selfieBtn = document.getElementById("uploadSelfieBtn");
    const folderInput = document.getElementById("folderUpload");
    const selfieInput = document.getElementById("selfieUpload");
    const previewContainer = document.getElementById("previewContainer");
    const matchedImages = document.getElementById("matchedImages");

    // Upload folder
    folderBtn.addEventListener("click", () => {
        folderInput.click();
    });

    // Upload selfie
    selfieBtn.addEventListener("click", () => {
        selfieInput.click();
    });

    // Handle folder upload
    folderInput.addEventListener("change", () => {
        const files = folderInput.files;
        if (files.length === 0) return;

        previewContainer.innerHTML = "";
        const formData = new FormData();
        for (const file of files) {
            formData.append("images", file);
        }

        for (const file of files) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement("img");
                img.src = e.target.result;
                previewContainer.appendChild(img);
            };
            reader.readAsDataURL(file);
        }

        fetch("/upload_folder", {
            method: "POST",
            body: formData,
        })
            .then(res => res.json())
            .then(data => {
                alert(data.message || "Folder uploaded");
            })
            .catch(err => {
                console.error(err);
                alert("Failed to upload folder.");
            });
    });

    // Handle selfie upload and show matches
    selfieInput.addEventListener("change", () => {
        const file = selfieInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        fetch("/upload_selfie", {
            method: "POST",
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                matchedImages.innerHTML = "";
                if (data.matches && data.matches.length > 0) {
                    data.matches.forEach(match => {
                        console.log("Single Image Match: ", match);
                        const img = document.createElement("img");
                        img.src = match.path // path
                        matchedImages.appendChild(img);
                    });
                } else {
                    matchedImages.innerHTML = "<p>No similar faces found.</p>";
                }
            })
            .catch(err => {
                console.error(err);
                alert("Failed to upload selfie.");
            });
    });
});
