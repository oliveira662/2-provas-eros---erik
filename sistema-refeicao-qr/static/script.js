// Scanner QR simples usando HTML5 e jsQR
// Para produção, usar html5-qrcode lib, mas para MVP básico

let video = document.getElementById('qr-video');
let canvas = document.getElementById('qr-canvas');
let ctx = canvas.getContext('2d');
let result = document.getElementById('qr-result');

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } }).then(function(stream) {
        video.srcObject = stream;
        video.play();
        requestAnimationFrame(tick);
    }).catch(function(err) {
        console.error('Erro câmera:', err);
        result.textContent = 'Erro ao acessar câmera. Use HTTPS para produção.';
    });
}

function tick() {
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);
        
        let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        let code = jsQR(imageData.data, imageData.width, imageData.height);
        
        if (code) {
            handleQrResult(code.data);
            return; // Para após primeiro scan
        }
    }
    requestAnimationFrame(tick);
}

// Fallback: parse manual para MVP (simula scan)
function handleQrResult(data) {
    if (data.startsWith('refeicao:')) {
        let refeicao_id = data.split(':')[1];
        result.innerHTML = `<a href="/confirmar/${refeicao_id}">Confirmar Refeição ID: ${refeicao_id}</a>`;
        result.style.color = 'green';
        result.style.fontSize = '1.2rem';
    } else {
        result.textContent = 'QR inválido: ' + data;
    }
}

// Nota: Para scan real, adicione <script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js"></script> em cantina.html
// Ou use biblioteca html5-qrcode para melhor suporte.
