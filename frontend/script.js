const buttons = document.querySelectorAll('.btn:not(.qr-modal *)');

buttons.forEach(button => {
    button.addEventListener('click', function(e) {
        if (this.tagName === 'BUTTON' && !this.closest('.qr-modal')) {
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 100);
        }
    });
});

const flipCard = document.querySelector('.flip-card');

if (flipCard) {
    flipCard.addEventListener('click', function() {
        this.classList.toggle('flipped');
    });
}

// ========================================
// FUNCIONALIDADE CONFIG.HTML
// ========================================

async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE_URL}/config`);
        const data = await response.json();

        if (data.success && data.data) {
            const sliderA = document.getElementById('slider-a');
            const sliderB = document.getElementById('slider-b');
            const sliderC = document.getElementById('slider-c');
            const valueA = document.getElementById('value-a');
            const valueB = document.getElementById('value-b');
            const valueC = document.getElementById('value-c');

            if (sliderA && valueA) {
                sliderA.value = Math.round(data.data.nivel_1_threshold * 100);
                valueA.textContent = sliderA.value;
            }
            if (sliderB && valueB) {
                sliderB.value = Math.round(data.data.nivel_2_threshold * 100);
                valueB.textContent = sliderB.value;
            }
            if (sliderC && valueC) {
                sliderC.value = Math.round(data.data.nivel_3_threshold * 100);
                valueC.textContent = sliderC.value;
            }
        }
    } catch (error) {
        // Falha silenciosa
    }
}

if (document.getElementById('slider-a')) {
    const sliderA = document.getElementById('slider-a');
    const valueA = document.getElementById('value-a');
    sliderA.addEventListener('input', function() {
        valueA.textContent = this.value;
    });

    loadConfig();
}

if (document.getElementById('slider-b')) {
    const sliderB = document.getElementById('slider-b');
    const valueB = document.getElementById('value-b');
    sliderB.addEventListener('input', function() {
        valueB.textContent = this.value;
    });
}

if (document.getElementById('slider-c')) {
    const sliderC = document.getElementById('slider-c');
    const valueC = document.getElementById('value-c');
    sliderC.addEventListener('input', function() {
        valueC.textContent = this.value;
    });
}

const saveButton = document.querySelector('.save-button');
if (saveButton) {
    saveButton.addEventListener('click', async function() {
        const valueAElement = document.getElementById('value-a');
        const valueBElement = document.getElementById('value-b');
        const valueCElement = document.getElementById('value-c');

        if (!valueAElement || !valueBElement || !valueCElement) return;

        const valueA = parseInt(valueAElement.textContent);
        const valueB = parseInt(valueBElement.textContent);
        const valueC = parseInt(valueCElement.textContent);

        const thresholds = {
            nivel_1_threshold: valueA / 100,
            nivel_2_threshold: valueB / 100,
            nivel_3_threshold: valueC / 100
        };

        saveButton.disabled = true;
        saveButton.textContent = 'Salvando...';

        try {
            const response = await fetch(`${API_BASE_URL}/config`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(thresholds)
            });

            const data = await response.json();

            if (data.success) {
                const toast = document.getElementById('toast');
                if (toast) {
                    const toastMessage = toast.querySelector('.toast-message') || toast;
                    if (toastMessage.textContent !== undefined) {
                        toastMessage.textContent = 'Configurações salvas com sucesso!';
                    }
                    toast.classList.add('show');
                    setTimeout(() => {
                        toast.classList.remove('show');
                    }, 3000);
                }
            } else {
                alert('Erro ao salvar configurações: ' + (data.error || data.message));
            }

        } catch (error) {
            alert('Erro ao conectar com o servidor. Verifique se o backend está rodando.');
        } finally {
            saveButton.disabled = false;
            saveButton.textContent = 'Salvar';
        }
    });
}

// ========================================
// FUNCIONALIDADE SIGNUP.HTML
// ========================================

let cameraStream = null;
let capturedImageData = null;

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const cameraVideo = document.getElementById('camera-stream');
const cameraCanvas = document.getElementById('camera-canvas');
const capturedImg = document.getElementById('captured-image');
const captureBtn = document.getElementById('capture-btn');
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const resetBtn = document.getElementById('reset-btn');
const signupForm = document.getElementById('signup-form');

if (cameraVideo) {
    navigator.mediaDevices.getUserMedia({
        video: {
            width: { ideal: 1280 },
            height: { ideal: 720 }
        }
    })
    .then(stream => {
        cameraStream = stream;
        cameraVideo.srcObject = stream;
    })
    .catch(error => {
        alert('Não foi possível acessar a câmera. Por favor, permita o acesso.');
    });
}

if (captureBtn) {
    captureBtn.addEventListener('click', function() {
        if (!cameraVideo || !cameraCanvas) return;

        const context = cameraCanvas.getContext('2d');
        cameraCanvas.width = cameraVideo.videoWidth;
        cameraCanvas.height = cameraVideo.videoHeight;
        context.drawImage(cameraVideo, 0, 0);

        capturedImageData = cameraCanvas.toDataURL('image/png');
        capturedImg.src = capturedImageData;

        cameraVideo.style.display = 'none';
        capturedImg.style.display = 'block';
        resetBtn.style.display = 'block';
    });
}

if (uploadBtn) {
    uploadBtn.addEventListener('click', function() {
        fileInput.click();
    });
}

if (fileInput) {
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(event) {
            capturedImageData = event.target.result;
            capturedImg.src = capturedImageData;

            if (cameraVideo) cameraVideo.style.display = 'none';
            capturedImg.style.display = 'block';
            if (resetBtn) resetBtn.style.display = 'block';
        };
        reader.readAsDataURL(file);
    });
}

if (resetBtn) {
    resetBtn.addEventListener('click', function() {
        capturedImageData = null;
        capturedImg.style.display = 'none';
        if (cameraVideo) cameraVideo.style.display = 'block';
        resetBtn.style.display = 'none';
    });
}

function showToast(message, type = 'success', duration = 3000) {
    const toast = document.getElementById('toast-signup') || document.getElementById('toast');
    if (!toast) return;

    const messageElement = toast.querySelector('.toast-message');
    if (messageElement) {
        messageElement.textContent = message;
    }

    toast.classList.remove('error', 'success');
    toast.classList.add('show', type);

    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

function setLoading(isLoading) {
    const submitBtn = document.querySelector('#signup-form button[type="submit"]');
    if (!submitBtn) return;

    if (isLoading) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Cadastrando...';
    } else {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Cadastrar';
    }
}

if (signupForm) {
    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const nameInput = document.getElementById('name-input');
        const securityLevel = document.querySelector('input[name="security-level"]:checked');

        if (!nameInput || !securityLevel) {
            showToast('Por favor, preencha todos os campos.', 'error');
            return;
        }

        if (!capturedImageData) {
            showToast('Por favor, capture ou faça upload de uma foto.', 'error');
            return;
        }

        const name = nameInput.value.trim();
        const level = parseInt(securityLevel.value);

        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/auth/enroll`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    security_level: level,
                    image: capturedImageData
                })
            });

            const data = await response.json();

            if (data.success) {
                // If server returned a QR code for MFA, store it and redirect
                // to a dedicated page that displays the QR code. This removes
                // the inline modal logic and avoids accidental immediate closure.
                if (data.data && data.data.qr_code) {
                    try {
                        sessionStorage.setItem('pending_qr', data.data.qr_code);
                        sessionStorage.setItem('pending_user', name);
                        // Navigate to the QR display page where the user can scan/save it
                        window.location.href = 'qrcode.html';
                    } catch (err) {
                        showToast('Erro ao preparar QR code localmente.', 'error', 5000);
                    }
                } else {
                    showToast(data.message, 'success');
                    setTimeout(() => {
                        signupForm.reset();
                        if (resetBtn) resetBtn.click();
                    }, 2000);
                }
            } else {
                showToast(data.error || data.message, 'error', 5000);
            }

        } catch (error) {
            showToast('Erro ao conectar com o servidor. Verifique se o backend está rodando.', 'error', 5000);
        } finally {
            setLoading(false);
        }
    });
}

// ========================================
// FUNCIONALIDADE SIGNIN.HTML
// ========================================

const cameraVideoSignin = document.getElementById('camera-stream-signin');
let authenticationInProgress = false;
let authenticationInterval = null;

async function authenticateFrame() {
    if (authenticationInProgress || !cameraVideoSignin) return;

    authenticationInProgress = true;

    try {
        const canvas = document.createElement('canvas');
        canvas.width = cameraVideoSignin.videoWidth;
        canvas.height = cameraVideoSignin.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(cameraVideoSignin, 0, 0);

        const imageData = canvas.toDataURL('image/jpeg', 0.8);

        const response = await fetch(`${API_BASE_URL}/auth/authenticate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData
            })
        });

        const data = await response.json();

        if (data.success) {
            if (authenticationInterval) {
                clearInterval(authenticationInterval);
                authenticationInterval = null;
            }

            localStorage.setItem('user_name', data.data.user);
            localStorage.setItem('user_level', data.data.permission_level);

            if (data.data.requires_mfa) {
                showMFAModal(data.data.user, data.data.permission_level);
            } else {
                window.location.href = 'dashboard.html?user=' + encodeURIComponent(data.data.user);
            }
        }

    } catch (error) {
        // Falha silenciosa
    } finally {
        authenticationInProgress = false;
    }
}

function showMFAModal(username, userLevel) {
    const modal = document.createElement('div');
    modal.className = 'mfa-modal';
    modal.innerHTML = `
        <div class="mfa-modal-content">
            <h3>Autenticação de Dois Fatores</h3>
            <p>Olá, <strong>${username}</strong>!</p>
            <p>Por favor, insira o código do Google Authenticator:</p>
            <input type="text" id="mfa-code-input" placeholder="000000" maxlength="6" pattern="[0-9]{6}" />
            <div class="mfa-buttons">
                <button id="mfa-verify-btn">Verificar</button>
                <button id="mfa-cancel-btn">Cancelar</button>
            </div>
            <p id="mfa-error" style="color: red; display: none;"></p>
        </div>
    `;
    document.body.appendChild(modal);

    const codeInput = document.getElementById('mfa-code-input');
    const verifyBtn = document.getElementById('mfa-verify-btn');
    const cancelBtn = document.getElementById('mfa-cancel-btn');
    const errorMsg = document.getElementById('mfa-error');

    codeInput.focus();

    verifyBtn.addEventListener('click', async () => {
        const code = codeInput.value.trim();

        if (code.length !== 6) {
            errorMsg.textContent = 'Código deve ter 6 dígitos';
            errorMsg.style.display = 'block';
            return;
        }

        verifyBtn.disabled = true;
        verifyBtn.textContent = 'Verificando...';

        try {
            const response = await fetch(`${API_BASE_URL}/auth/verify-mfa`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    otp_code: code
                })
            });

            const data = await response.json();

            if (data.success) {
                modal.remove();
                window.location.href = 'dashboard.html?user=' + encodeURIComponent(username);
            } else {
                errorMsg.textContent = data.error || 'Código inválido';
                errorMsg.style.display = 'block';
                verifyBtn.disabled = false;
                verifyBtn.textContent = 'Verificar';
                codeInput.value = '';
                codeInput.focus();
            }

        } catch (error) {
            errorMsg.textContent = 'Erro ao conectar com servidor';
            errorMsg.style.display = 'block';
            verifyBtn.disabled = false;
            verifyBtn.textContent = 'Verificar';
        }
    });

    codeInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            verifyBtn.click();
        }
    });

    cancelBtn.addEventListener('click', () => {
        modal.remove();
        if (!authenticationInterval) {
            authenticationInterval = setInterval(authenticateFrame, 3000);
        }
    });
}

if (cameraVideoSignin) {
    navigator.mediaDevices.getUserMedia({
        video: {
            width: { ideal: 1280 },
            height: { ideal: 720 }
        }
    })
    .then(stream => {
        cameraVideoSignin.srcObject = stream;

        cameraVideoSignin.addEventListener('loadedmetadata', () => {
            authenticationInterval = setInterval(authenticateFrame, 3000);
        });
    })
    .catch(error => {
        alert('Não foi possível acessar a câmera. Por favor, permita o acesso.');
    });
}
