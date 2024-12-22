document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('#video');
    const uploadForm = document.querySelector('form');
    const progressBar = document.querySelector('.upload-progress-bar');
    const progressContainer = document.querySelector('.upload-progress');
    const uploadInfo = document.querySelector('.upload-info');

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);

    // File input change event
    fileInput.addEventListener('change', handleFileSelect);

    // Form submit event
    uploadForm.addEventListener('submit', handleSubmit);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        uploadArea.classList.add('highlight');
    }

    function unhighlight(e) {
        uploadArea.classList.remove('highlight');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect();
        }
    }

    function handleFileSelect() {
        const file = fileInput.files[0];
        if (file) {
            // Verificar se é um arquivo de vídeo
            if (!file.type.startsWith('video/')) {
                alert('Por favor, selecione um arquivo de vídeo.');
                fileInput.value = '';
                return;
            }

            // Verificar tamanho do arquivo (100MB em bytes)
            if (file.size > 100 * 1024 * 1024) {
                alert('O arquivo é muito grande. O tamanho máximo é 100MB.');
                fileInput.value = '';
                return;
            }

            // Atualizar a informação do arquivo
            uploadInfo.innerHTML = `
                Arquivo selecionado: ${file.name}<br>
                <small>Tamanho: ${formatFileSize(file.size)}</small>
            `;
        }
    }

    function handleSubmit(e) {
        e.preventDefault();

        const formData = new FormData(uploadForm);
        
        // Mostrar barra de progresso
        progressContainer.style.display = 'block';
        
        // Fazer upload com XMLHttpRequest para mostrar progresso
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressBar.style.width = percentComplete + '%';
            }
        });

        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    window.location.href = '/';  // Redirecionar para a página inicial
                } else {
                    alert('Erro ao fazer upload: ' + response.message);
                }
            } else {
                alert('Erro ao fazer upload. Por favor, tente novamente.');
            }
        });

        xhr.addEventListener('error', function() {
            alert('Erro na conexão. Por favor, tente novamente.');
        });

        xhr.open('POST', uploadForm.action || window.location.href, true);
        xhr.send(formData);
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
});
