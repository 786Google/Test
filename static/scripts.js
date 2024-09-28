document.getElementById('upload-button').addEventListener('click', async () => {
    const files = document.getElementById('file-input').files;
    const prompt = document.getElementById('prompt-input').value;
    const uploadStatus = document.getElementById('upload-status');
    uploadStatus.innerHTML = '';

    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }
    formData.append('prompt', prompt);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });
    const results = await response.json();

    results.forEach(file => {
        const statusDiv = document.createElement('div');
        const thumbnailDiv = document.createElement('div');
        thumbnailDiv.className = 'thumbnail';

        const uploadingDiv = document.createElement('div');
        uploadingDiv.className = 'uploading-animation';
        uploadingDiv.innerText = 'UPLOADING...';

        thumbnailDiv.appendChild(uploadingDiv);
        uploadStatus.appendChild(thumbnailDiv);

        setTimeout(() => {
            uploadingDiv.innerText = 'PROCESSED';
        }, 2000);
    });
});
