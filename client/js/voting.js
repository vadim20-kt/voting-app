// Voting System - Versiune completă și modernă
class VotingSystem {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentUser = null;
        this.sessions = [];
        this.init();
    }

    async init() {
        // Verifică autentificarea
        if (!await this.checkVoterAuth()) {
            return;
        }

        // Inițializează interfața
        this.setupEventListeners();
        this.loadUserInfo();
        await this.loadVotingSessions();
    }

    async checkVoterAuth() {
        const userData = localStorage.getItem('userData');
        
        if (!userData) {
            window.location.href = '/login';
            return false;
        }

        try {
            this.currentUser = JSON.parse(userData);
            
            // Verifică dacă userul este admin
            if (this.currentUser.is_admin) {
                window.location.href = '/admin';
                return false;
            }
            return true;
        } catch (error) {
            console.error('Error parsing user data:', error);
            this.logout();
            return false;
        }
    }

    setupEventListeners() {
        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadVotingSessions());
        }

        // Modal close
        const modalClose = document.getElementById('modalClose');
        const voteModal = document.getElementById('voteModal');
        
        if (modalClose) {
            modalClose.addEventListener('click', () => {
                voteModal.style.display = 'none';
            });
        }

        // Close modal on outside click
        if (voteModal) {
            voteModal.addEventListener('click', (e) => {
                if (e.target === voteModal) {
                    voteModal.style.display = 'none';
                }
            });
        }

        // Mobile menu toggle
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navToggle.classList.toggle('active');
            });
        }
    }

    loadUserInfo() {
        if (this.currentUser) {
            const userNameEl = document.getElementById('userName');
            const userWelcomeEl = document.getElementById('userWelcome');
            
            if (userNameEl) {
                userNameEl.textContent = this.currentUser.nume || 'Utilizator';
            }
            
            if (userWelcomeEl) {
                userWelcomeEl.innerHTML = `
                    <i class="fas fa-user-circle"></i>
                    <span>${this.currentUser.nume || 'Utilizator'}</span>
                `;
            }
        }
    }

    async loadVotingSessions() {
        const sessionsList = document.getElementById('sessionsList');
        const refreshBtn = document.getElementById('refreshBtn');
        
        if (!sessionsList) return;

        // Show loading state
        sessionsList.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Se încarcă sesiunile...</p>
            </div>
        `;

        if (refreshBtn) {
            refreshBtn.classList.add('spinning');
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/sessions/active`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const sessions = await response.json();
            this.sessions = sessions;
            
            this.displaySessions(sessions);
            this.updateStats(sessions.length);
            
        } catch (error) {
            console.error('Eroare la încărcarea sesiunilor:', error);
            sessionsList.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Eroare la încărcarea sesiunilor</p>
                    <button class="btn-primary" onclick="votingSystem.loadVotingSessions()">
                        <i class="fas fa-redo"></i> Reîncearcă
                    </button>
                </div>
            `;
            this.showToast('Eroare la încărcarea sesiunilor. Verifică conexiunea la server.', 'error');
        } finally {
            if (refreshBtn) {
                refreshBtn.classList.remove('spinning');
            }
        }
    }

    displaySessions(sessions) {
        const sessionsList = document.getElementById('sessionsList');
        if (!sessionsList) return;

        if (!sessions || sessions.length === 0) {
            sessionsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h3>Nu există sesiuni active</h3>
                    <p>Momentan nu sunt sesiuni de vot disponibile. Verifică mai târziu!</p>
                </div>
            `;
            return;
        }

        sessionsList.innerHTML = sessions.map(session => `
            <div class="session-card" data-session-id="${session.id}">
                <div class="session-header">
                    <h3 class="session-title">
                        <i class="fas fa-poll"></i>
                        ${this.escapeHtml(session.titlu || 'Sesiune fără titlu')}
                    </h3>
                    <span class="session-badge active">
                        <i class="fas fa-circle"></i> Activă
                    </span>
                </div>
                ${session.descriere ? `
                    <p class="session-description">${this.escapeHtml(session.descriere)}</p>
                ` : ''}
                <div class="session-meta">
                    <div class="meta-item">
                        <i class="fas fa-list"></i>
                        <span>${session.num_options || 0} opțiuni</span>
                    </div>
                    ${session.data_start ? `
                        <div class="meta-item">
                            <i class="fas fa-calendar-alt"></i>
                            <span>${this.formatDate(session.data_start)}</span>
                        </div>
                    ` : ''}
                </div>
                <div class="session-actions">
                    <button class="btn-primary btn-vote" onclick="votingSystem.openVoteModal(${session.id})">
                        <i class="fas fa-vote-yea"></i>
                        Votează acum
                    </button>
                </div>
            </div>
        `).join('');
    }

    async openVoteModal(sessionId) {
        const modal = document.getElementById('voteModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalDescription = document.getElementById('modalDescription');
        const optionsList = document.getElementById('optionsList');

        if (!modal || !modalTitle || !optionsList) return;

        // Show loading
        optionsList.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Se încarcă opțiunile...</p>
            </div>
        `;
        modal.style.display = 'flex';

        try {
            // Load session details
            const sessionResponse = await fetch(`${this.apiBaseUrl}/sessions/${sessionId}`);
            let sessionData = null;
            
            if (sessionResponse.ok) {
                sessionData = await sessionResponse.json();
            }

            // Load options
            const optionsResponse = await fetch(`${this.apiBaseUrl}/sessions/${sessionId}/options`);
            
            if (!optionsResponse.ok) {
                throw new Error(`HTTP error! status: ${optionsResponse.status}`);
            }
            
            const options = await optionsResponse.json();

            if (!options || options.length === 0) {
                optionsList.innerHTML = `
                    <div class="error-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Nu există opțiuni disponibile pentru această sesiune</p>
                    </div>
                `;
                return;
            }

            // Update modal title
            if (sessionData && sessionData.titlu) {
                modalTitle.innerHTML = `
                    <i class="fas fa-vote-yea"></i>
                    ${this.escapeHtml(sessionData.titlu)}
                `;
            }

            // Update description
            if (sessionData && sessionData.descriere) {
                modalDescription.innerHTML = `<p>${this.escapeHtml(sessionData.descriere)}</p>`;
            } else {
                modalDescription.innerHTML = '';
            }

            // Display options
            optionsList.innerHTML = options.map((option, index) => `
                <div class="option-item">
                    <input 
                        type="radio" 
                        name="voteOption" 
                        value="${option.id}" 
                        id="option_${option.id}"
                        ${index === 0 ? 'checked' : ''}
                    >
                    <label for="option_${option.id}" class="option-label">
                        <div class="option-radio"></div>
                        <span class="option-name">${this.escapeHtml(option.text_optiune || option.nume || 'Opțiune')}</span>
                    </label>
                </div>
            `).join('') + `
                <div class="modal-actions">
                    <button class="btn-secondary" onclick="document.getElementById('voteModal').style.display='none'">
                        <i class="fas fa-times"></i> Anulează
                    </button>
                    <button class="btn-primary btn-confirm-vote" onclick="votingSystem.submitVote(${sessionId})">
                        <i class="fas fa-check"></i> Confirmă votul
                    </button>
                </div>
            `;

        } catch (error) {
            console.error('Eroare la deschiderea modalului:', error);
            optionsList.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Eroare la încărcarea opțiunilor de vot</p>
                    <button class="btn-primary" onclick="votingSystem.openVoteModal(${sessionId})">
                        <i class="fas fa-redo"></i> Reîncearcă
                    </button>
                </div>
            `;
            this.showToast('Eroare la încărcarea opțiunilor de vot', 'error');
        }
    }

    async submitVote(sessionId) {
        const selectedOption = document.querySelector('input[name="voteOption"]:checked');
        
        if (!selectedOption) {
            this.showToast('Vă rugăm să selectați o opțiune!', 'error');
            return;
        }

        const optionId = selectedOption.value;
        const confirmBtn = document.querySelector('.btn-confirm-vote');
        
        if (!confirmBtn) return;

        // Disable button and show loading
        const originalHtml = confirmBtn.innerHTML;
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Se procesează...';

        try {
            const response = await fetch(`${this.apiBaseUrl}/vote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.currentUser.id,
                    option_id: parseInt(optionId)
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Eroare la trimiterea votului');
            }

            // Success
            this.showToast('Votul a fost înregistrat cu succes!', 'success');
            
            // Close modal
            document.getElementById('voteModal').style.display = 'none';
            
            // Reload sessions
            setTimeout(() => {
                this.loadVotingSessions();
            }, 1500);

        } catch (error) {
            console.error('Eroare la trimiterea votului:', error);
            this.showToast(error.message || 'Eroare la trimiterea votului', 'error');
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalHtml;
        }
    }

    updateStats(count) {
        const activeSessionsCount = document.getElementById('activeSessionsCount');
        if (activeSessionsCount) {
            activeSessionsCount.textContent = count;
        }
    }

    logout() {
        localStorage.removeItem('userData');
        localStorage.removeItem('adminData');
        window.location.href = '/login';
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };

        toast.innerHTML = `
            <i class="fas fa-${icons[type] || icons.info}"></i>
            <span>${this.escapeHtml(message)}</span>
        `;

        container.appendChild(toast);

        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);

        // Remove after delay
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('ro-RO', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Initialize voting system
let votingSystem;
document.addEventListener('DOMContentLoaded', () => {
    votingSystem = new VotingSystem();
});
