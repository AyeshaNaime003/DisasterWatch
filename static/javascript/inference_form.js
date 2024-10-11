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
            label.innerHTML = `<i>${fileName}</i>`;
        } 
        // else {
        //     label.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><path d="M288 109.3V352c0 17.7-14.3 32-32 32s-32-14.3-32-32V109.3l-73.4 73.4c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3l128-128c12.5-12.5 32.8-12.5 45.3 0l128 128c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L288 109.3zM64 352H192c0 35.3 28.7 64 64 64s64-28.7 64-64H448c35.3 0 64 28.7 64 64v32c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V416c0-35.3 28.7-64 64-64zM432 456a24 24 0 1 0 0-48 24 24 0 1 0 0 48z"/></svg>
        //     <i> Drop or drag a file here or 
        //     <br><b>Click to browse</b></br></i>`;
        // }
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
