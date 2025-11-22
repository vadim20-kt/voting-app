class AuthSystem {
    static async loginUser(credentials) {
        try {
            console.log('Încerc login cu:', credentials);
            
            const response = await fetch('/api/login', {  // Folosește path relativ
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            const result = await response.json();
            
            // Verifică dacă este necesar cod de verificare
            if (result.requires_verification) {
                return { 
                    success: false, 
                    requires_verification: true,
                    message: result.message || 'Cod de verificare necesar'
                    // Nu mai returnăm codul - doar în consola serverului
                };
            }

            if (!response.ok) {
                throw new Error(result.error || 'Eroare la autentificare');
            }
            
            if (result.success) {
                // Salvează datele utilizatorului
                localStorage.setItem('userData', JSON.stringify(result.user));
                
                // REDIRECȚIONARE CORECTĂ
                if (result.user.is_admin) {
                    window.location.href = 'index.html'; // Pagina principală pentru admin
                } else {
                    window.location.href = 'dashboard.html'; // Panou votant
                }
                
                return { success: true, user: result.user };
            } else {
                throw new Error(result.error || 'Autentificare eșuată');
            }

        } catch (error) {
            console.error('Eroare login:', error);
            return { success: false, error: error.message };
        }
    }

    static async verifyCode(idnp, code) {
        try {
            const response = await fetch('/api/verify-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ idnp, code })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Eroare verificare cod:', error);
            return { success: false, error: error.message };
        }
    }

    static async requestVerificationCode(idnp, verificationMethod = 'email') {
        try {
            const response = await fetch('/api/request-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ idnp, verification_method: verificationMethod })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Eroare cerere cod:', error);
            return { success: false, error: error.message };
        }
    }


    static async registerUser(userData) {
        try {
            console.log('Încerc înregistrare cu:', userData);
            
            const response = await fetch('http://localhost:5000/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Eroare la înregistrare');
            }

            const result = await response.json();
            return { success: true, message: result.message };
        } catch (error) {
            console.error('Eroare înregistrare:', error);
            return { success: false, error: error.message };
        }
    }

    static logout() {
        // Curăță toate datele de autentificare
        localStorage.removeItem('userData');
        localStorage.removeItem('adminData');
        localStorage.removeItem('token');
        
        // Redirect către pagina principală
        window.location.href = '/index.html';
    }

    static getCurrentUser() {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    }

    static isAuthenticated() {
        return !!this.getCurrentUser();
    }

    static isAdmin() {
        const user = this.getCurrentUser();
        return user && user.is_admin === true;
    }

    static requireAuth(redirectTo = 'login.html') {
        if (!this.isAuthenticated()) {
            window.location.href = redirectTo;
            return false;
        }
        return true;
    }

    static requireAdmin(redirectTo = 'login.html') {
        if (!this.isAuthenticated() || !this.isAdmin()) {
            window.location.href = redirectTo;
            return false;
        }
        return true;
    }
}

// Admin Authentication
class AdminAuth {
    static getAdminData() {
        const adminData = localStorage.getItem('adminData');
        return adminData ? JSON.parse(adminData) : null;
    }

    static setAdminData(adminData) {
        localStorage.setItem('adminData', JSON.stringify(adminData));
    }

    static getAuthHeaders() {
        const adminData = this.getAdminData();
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${adminData?.token || ''}`
        };
    }

    static logout() {
        localStorage.removeItem('adminData');
        localStorage.removeItem('userData');
        window.location.href = 'login.html';
    }

    static isAuthenticated() {
        const adminData = this.getAdminData();
        return !!(adminData && adminData.rol === 'admin');
    }
}

// Evenimente pentru login.html
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    // Toggle între login/register
    document.getElementById('showRegister')?.addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('loginSection').style.display = 'none';
        document.getElementById('registerSection').style.display = 'block';
    });
    
    document.getElementById('showLogin')?.addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('registerSection').style.display = 'none';
        document.getElementById('loginSection').style.display = 'block';
    });
    
    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    });
    
    // Login form
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const verificationCode = document.getElementById('verificationCodeInput')?.value;
            const verificationSection = document.getElementById('verificationSection');
            const isVerificationStep = verificationSection && verificationSection.style.display !== 'none';
            
            const credentials = {
                idnp: formData.get('idnp'),
                parola: formData.get('parola')
            };
            
            // Dacă este pasul de verificare, adaugă codul
            if (isVerificationStep && verificationCode) {
                credentials.verification_code = verificationCode;
            } else if (isVerificationStep) {
                // Dacă secțiunea de verificare este vizibilă, cere metoda de trimitere
                const verificationMethod = document.querySelector('input[name="verificationMethod"]:checked')?.value || 'email';
                credentials.verification_method = verificationMethod;
            }
            
            // Validate IDNP
            if (!/^\d{13}$/.test(credentials.idnp)) {
                showMessage('IDNP trebuie să conțină exact 13 cifre!', 'error');
                return;
            }
            
            // Validate verification code if provided
            if (isVerificationStep && verificationCode && !/^\d{6}$/.test(verificationCode)) {
                showMessage('Codul de verificare trebuie să conțină exact 6 cifre!', 'error');
                return;
            }
            
            const submitBtn = document.getElementById('loginSubmitBtn');
            const submitText = document.getElementById('loginSubmitText');
            const originalText = submitBtn.innerHTML;
            
            if (isVerificationStep) {
                submitText.textContent = 'Se verifică...';
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span id="loginSubmitText">Se verifică...</span>';
            } else {
                submitText.textContent = 'Se autentifică...';
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span id="loginSubmitText">Se autentifică...</span>';
            }
            submitBtn.disabled = true;
            
            try {
                const result = await AuthSystem.loginUser(credentials);
                
                if (result.requires_verification && !isVerificationStep) {
                    // Afișează secțiunea de verificare cod în formular
                    verificationSection.style.display = 'block';
                    const methodText = document.getElementById('verificationMethodText');
                    const selectedMethod = document.querySelector('input[name="verificationMethod"]:checked')?.value || 'email';
                    methodText.textContent = selectedMethod === 'email' ? 'email-ul' : 'SMS-ul';
                    
                    // Actualizează textul butonului
                    submitText.textContent = 'Verifică Cod';
                    submitBtn.innerHTML = '<i class="fas fa-shield-alt"></i> <span id="loginSubmitText">Verifică Cod</span>';
                    
                    // Focus pe input-ul de cod
                    document.getElementById('verificationCodeInput')?.focus();
                    
                    showMessage(result.message || 'Cod de verificare trimis. Verifică email-ul sau SMS-ul.', 'success');
                    submitBtn.disabled = false;
                } else if (result.success) {
                    showMessage('Autentificare reușită! Redirecționare...', 'success');
                    
                    setTimeout(() => {
                        if (result.user.is_admin) {
                            window.location.href = 'index.html';
                        } else {
                            window.location.href = 'dashboard.html';
                        }
                    }, 1500);
                } else {
                    showMessage('Eroare: ' + result.error, 'error');
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            } catch (error) {
                showMessage('Eroare de conexiune: ' + error.message, 'error');
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
        
        // Actualizează textul metodei când se schimbă selecția
        document.querySelectorAll('input[name="verificationMethod"]').forEach(radio => {
            radio.addEventListener('change', function() {
                const methodText = document.getElementById('verificationMethodText');
                if (methodText) {
                    methodText.textContent = this.value === 'email' ? 'email-ul' : 'SMS-ul';
                }
            });
        });
    }
    
    // Code verification form
    const codeForm = document.getElementById('codeForm');
    if (codeForm) {
        codeForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const idnp = document.getElementById('selectedIdnp').value;
            const password = document.getElementById('selectedPassword').value;
            const code = document.getElementById('verificationCode').value;
            
            if (!/^\d{6}$/.test(code)) {
                showMessage('Codul trebuie să conțină exact 6 cifre!', 'error');
                return;
            }
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Se verifică...';
            submitBtn.disabled = true;
            
            try {
                // Trimite login cu cod de verificare
                const result = await AuthSystem.loginUser({
                    idnp: idnp,
                    parola: password,
                    verification_code: code
                });
                
                if (result.success) {
                    showMessage('Verificare reușită! Autentificare completă...', 'success');
                    
                    setTimeout(() => {
                        if (result.user.is_admin) {
                            window.location.href = 'index.html';
                        } else {
                            window.location.href = 'dashboard.html';
                        }
                    }, 1500);
                } else {
                    showMessage('Eroare: ' + result.error, 'error');
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            } catch (error) {
                showMessage('Eroare de conexiune: ' + error.message, 'error');
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }
    
    // Request new code
    document.getElementById('resendCodeLink')?.addEventListener('click', async function(e) {
        e.preventDefault();
        
        const idnp = document.getElementById('loginIdnp')?.value || document.querySelector('input[name="idnp"]')?.value;
        if (!idnp) {
            showMessage('Eroare: IDNP lipsă', 'error');
            return;
        }
        
        const verificationMethod = document.querySelector('input[name="verificationMethod"]:checked')?.value || 'email';
        
        const link = this;
        const originalText = link.innerHTML;
        link.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Se trimite...';
        link.style.pointerEvents = 'none';
        
        try {
            const result = await AuthSystem.requestVerificationCode(idnp, verificationMethod);
            
            if (result.success) {
                showMessage(result.message || 'Cod nou trimis! Verifică email-ul sau SMS-ul.', 'success');
                
                // Resetează input-ul de cod
                document.getElementById('verificationCodeInput').value = '';
                document.getElementById('verificationCodeInput').focus();
            } else {
                showMessage('Eroare: ' + result.error, 'error');
            }
        } catch (error) {
            showMessage('Eroare de conexiune: ' + error.message, 'error');
        } finally {
            link.innerHTML = originalText;
            link.style.pointerEvents = 'auto';
        }
    });
    
    // Back to login
    document.getElementById('backToLogin')?.addEventListener('click', function(e) {
        e.preventDefault();
        showSection('login');
        document.getElementById('codeInfo').style.display = 'none';
        document.getElementById('verificationCode').value = '';
    });
    
    // Register form
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const userData = {
                idnp: formData.get('idnp'),
                nume: formData.get('nume'),
                email: formData.get('email'),
                telefon: formData.get('telefon'),
                parola: formData.get('parola')
            };
            
            // Validations
            if (!/^\d{13}$/.test(userData.idnp)) {
                showMessage('IDNP trebuie să conțină exact 13 cifre!', 'error');
                return;
            }
            
            const password = userData.parola;
            const confirmPassword = document.getElementById('regConfirmPassword').value;
            
            if (password !== confirmPassword) {
                showMessage('Parolele nu coincid!', 'error');
                return;
            }
            
            if (password.length < 6) {
                showMessage('Parola trebuie să aibă minim 6 caractere!', 'error');
                return;
            }
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Se înregistrează...';
            submitBtn.disabled = true;
            
            try {
                const result = await AuthSystem.registerUser(userData);
                
                if (result.success) {
                    showMessage(result.message, 'success');
                    
                    setTimeout(() => {
                        showSection('login');
                        document.getElementById('loginIdnp').value = userData.idnp;
                    }, 2000);
                } else {
                    showMessage('Eroare: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('Eroare de conexiune: ' + error.message, 'error');
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }
    
    function showSection(sectionName) {
        document.getElementById('loginSection').style.display = 'none';
        document.getElementById('registerSection').style.display = 'none';
        document.getElementById('codeSection').style.display = 'none';
        
        if (sectionName === 'login') {
            document.getElementById('loginSection').style.display = 'block';
        } else if (sectionName === 'register') {
            document.getElementById('registerSection').style.display = 'block';
        }
    }
    
    function showMessage(message, type) {
        const existingMessages = document.querySelectorAll('.auth-message');
        existingMessages.forEach(msg => msg.remove());
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `auth-message message-${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            ${message}
        `;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => {
            if (messageDiv.parentElement) {
                messageDiv.remove();
            }
        }, 5000);
    }
});