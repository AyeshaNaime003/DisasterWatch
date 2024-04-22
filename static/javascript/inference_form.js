document.addEventListener("DOMContentLoaded", function() {
    // Function to handle file drop
    function handleFileDrop(dropArea, fileInput) {
        dropArea.addEventListener("dragover", function(event) {
            event.preventDefault();
            dropArea.classList.add("dragover");
        });

        dropArea.addEventListener("dragleave", function(event) {
            event.preventDefault();
            dropArea.classList.remove("dragover");
        });

        dropArea.addEventListener("drop", function(event) {
            event.preventDefault();
            dropArea.classList.remove("dragover");
            const files = event.dataTransfer.files;
            const allowedExtensions = ["tif", "tiff"];
            const fileExtension = files[0].name.split(".").pop().toLowerCase();
            if (allowedExtensions.includes(fileExtension)) {
                fileInput.files = files;
                displayFileName(dropArea, files[0].name); // Display file name
            } else {
                alert("Please upload a TIF file.");
            }
        });

        // Click event for entire box
        dropArea.addEventListener("click", function() {
            fileInput.click();
        });

        // Change event for file input
        fileInput.addEventListener("change", function() {
            const allowedExtensions = ["tif", "tiff"];
            const fileExtension = fileInput.files[0].name.split(".").pop().toLowerCase();
            if (allowedExtensions.includes(fileExtension)) {
                dropArea.classList.remove("dragover");
                displayFileName(dropArea, fileInput.files[0].name); // Display file name
            } else {
                alert("Please upload a TIF file.");
                fileInput.value = ""; // Clear the input field
            }
        });
    }

    // Function to display file name
    function displayFileName(dropArea, fileName) {
        const label = dropArea.querySelector("label");
        if (fileName) {
            label.innerHTML = `<i class="fas fa-upload" style="font-weight:normal">${fileName}</i>`;
        } else {
            label.innerHTML = `<i class="fas fa-upload" style="font-weight:normal"> Drop or drag a file here or 
            <br><b>Click to browse</b></br></i>`;
        }
    }

    // Initialize file drop functionality for both image input fields
    const preImageDropArea = document.getElementById("pre_image_drop_area");
    const preImageInput = document.getElementById("pre_image");
    handleFileDrop(preImageDropArea, preImageInput);

    const postImageDropArea = document.getElementById("post_image_drop_area");
    const postImageInput = document.getElementById("post_image");
    handleFileDrop(postImageDropArea, postImageInput);

    // Display file name if already selected
    displayFileName(preImageDropArea, preImageInput.files[0] ? preImageInput.files[0].name : null);
    displayFileName(postImageDropArea, postImageInput.files[0] ? postImageInput.files[0].name : null);
});
