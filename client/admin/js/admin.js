// Admin Panel - Versiune completă cu toate funcționalitățile
class AdminPanel {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Verifică dacă utilizatorul este admin
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        
        if (!userData.is_admin) {
            alert('Acces restricționat! Nu aveți drepturi de administrator.');
            window.location.href = '/dashboard';
            return;
        }

        this.currentUser = userData;
        console.log('✅ Panou admin inițializat pentru:', userData.nume);
        
        this.setupEventListeners();
        this.setupTabs();
        await this.loadDashboardData();
    }

    setupEventListeners() {
        // Logout
        document.getElementById('logoutBtn')?.addEventListener('click', () => {
            if (confirm('Sigur doriți să vă deconectați?')) {
                AuthSystem.logout();
            }
        });

        // Mobile menu toggle
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.querySelector('.admin-navbar .nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navToggle.classList.toggle('active');
            });
        }

        // Quick action buttons
        document.getElementById('quickSessionBtn')?.addEventListener('click', () => {
            this.switchTab('sessions');
            setTimeout(() => this.openSessionModal(), 100);
        });
        document.getElementById('quickNewsBtn')?.addEventListener('click', () => {
            this.switchTab('news');
            setTimeout(() => this.openNewsModal(), 100);
        });
        document.getElementById('quickResultBtn')?.addEventListener('click', () => {
            this.switchTab('results');
            setTimeout(() => this.openResultModal(), 100);
        });
        document.getElementById('refreshStatsBtn')?.addEventListener('click', () => this.loadStats());

        // Section action buttons
        document.getElementById('createSessionBtn')?.addEventListener('click', () => this.openSessionModal());
        document.getElementById('refreshSessionsBtn')?.addEventListener('click', () => this.loadSessions());
        document.getElementById('createNewsBtn')?.addEventListener('click', () => this.openNewsModal());
        document.getElementById('refreshNewsBtn')?.addEventListener('click', () => this.loadNews());
        document.getElementById('createResultBtn')?.addEventListener('click', () => this.openResultModal());
        document.getElementById('refreshResultsBtn')?.addEventListener('click', () => this.loadResults());
        document.getElementById('refreshUsersBtn')?.addEventListener('click', () => this.loadUsers());

        // Modal close buttons
        document.getElementById('closeSessionModalBtn')?.addEventListener('click', () => this.closeSessionModal());
        document.getElementById('cancelSessionBtn')?.addEventListener('click', () => this.closeSessionModal());
        document.getElementById('closeNewsModalBtn')?.addEventListener('click', () => this.closeNewsModal());
        document.getElementById('cancelNewsBtn')?.addEventListener('click', () => this.closeNewsModal());
        document.getElementById('closeResultModalBtn')?.addEventListener('click', () => this.closeResultModal());
        document.getElementById('cancelResultBtn')?.addEventListener('click', () => this.closeResultModal());

        // Session form
        document.getElementById('sessionForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSession();
        });

        // News form
        document.getElementById('newsForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveNews();
        });

        // Result form
        document.getElementById('resultForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveResult();
        });

        // Modal close on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });

        // Update admin name
        if (this.currentUser && this.currentUser.nume) {
            const adminNameEl = document.getElementById('adminName');
            if (adminNameEl) {
                adminNameEl.textContent = this.currentUser.nume;
            }
        }

        // Event delegation for dynamic buttons
        document.addEventListener('click', (e) => {
            const action = e.target.closest('[data-action]');
            if (!action) return;

            const actionType = action.dataset.action;
            const id = parseInt(action.dataset.id);

            switch(actionType) {
                case 'edit-session':
                    this.editSession(id);
                    break;
                case 'delete-session':
                    this.deleteSession(id);
                    break;
                case 'view-results':
                    this.viewSessionResults(id);
                    break;
                case 'edit-news':
                    this.editNews(id);
                    break;
                case 'delete-news':
                    this.deleteNews(id);
                    break;
                case 'edit-result':
                    this.editResult(id);
                    break;
                case 'delete-result':
                    this.deleteResult(id);
                    break;
                case 'delete-user':
                    this.deleteUser(id);
                    break;
            }
        });
    }

    setupTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tabName = btn.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `tab-${tabName}`);
        });

        // Load data for active tab
        if (tabName === 'sessions') {
            this.loadSessions();
        } else if (tabName === 'news') {
            this.loadNews();
        } else if (tabName === 'results') {
            this.loadResults();
        } else if (tabName === 'users') {
            this.loadUsers();
        }
    }

    async loadDashboardData() {
        try {
            // Încarcă toate datele pentru a actualiza statisticile și badge-urile
            await Promise.all([
                this.loadStats(),
                this.loadSessions(),
                this.loadNews(),
                this.loadResults(),
                this.loadUsers()
            ]);
        } catch (error) {
            console.error('❌ Eroare la încărcarea datelor:', error);
            this.showToast('Eroare la încărcarea datelor', 'error');
        }
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/stats`);
            if (response.ok) {
                const stats = await response.json();
                this.updateStatsUI(stats);
            }
        } catch (error) {
            console.error('❌ Eroare stats:', error);
        }
    }

    updateStatsUI(stats) {
        // Actualizează toate statisticile
        const totalUsersEl = document.getElementById('totalUsers');
        const activeSessionsEl = document.getElementById('activeSessions');
        const totalVotesEl = document.getElementById('totalVotes');
        const todayVotesEl = document.getElementById('todayVotes');
        const totalNewsEl = document.getElementById('totalNews');
        const activeNewsTextEl = document.getElementById('activeNewsText');
        const totalResultsEl = document.getElementById('totalResults');
        
        if (totalUsersEl) totalUsersEl.textContent = stats.total_users || 0;
        if (activeSessionsEl) activeSessionsEl.textContent = stats.active_sessions || 0;
        if (totalVotesEl) totalVotesEl.textContent = stats.total_votes || 0;
        if (todayVotesEl) todayVotesEl.textContent = stats.today_votes || 0;
        if (totalNewsEl) totalNewsEl.textContent = stats.total_news || 0;
        if (activeNewsTextEl) activeNewsTextEl.textContent = `${stats.active_news || 0} Active`;
        if (totalResultsEl) totalResultsEl.textContent = stats.total_results || 0;
        
        console.log('📊 Statistici actualizate:', stats);
    }

    // ===== SESIUNI =====
    async loadSessions() {
        const container = document.getElementById('sessionsList');
        if (!container) return;

        container.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Se încarcă sesiunile...</p></div>';

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/sessions`);
            if (response.ok) {
                const sessions = await response.json();
                this.displaySessions(sessions);
            } else {
                container.innerHTML = '<div class="empty-state">Eroare la încărcarea sesiunilor</div>';
            }
        } catch (error) {
            console.error('❌ Eroare sesiuni:', error);
            container.innerHTML = '<div class="empty-state">Eroare la încărcarea sesiunilor</div>';
        }
    }

    displaySessions(sessions) {
        const container = document.getElementById('sessionsList');
        if (!sessions || sessions.length === 0) {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><p>Nu există sesiuni de vot.</p></div>';
            this.updateBadge('sessionsBadge', 0);
            return;
        }

        this.updateBadge('sessionsBadge', sessions.length);

        container.innerHTML = sessions.map(session => `
            <div class="item-card">
                <div class="item-header">
                    <h3>${this.escapeHtml(session.titlu)}</h3>
                    <span class="badge ${session.status}">${session.status || 'active'}</span>
                </div>
                ${session.descriere ? `<p class="item-description">${this.escapeHtml(session.descriere)}</p>` : ''}
                <div class="item-meta">
                    <span><i class="fas fa-list"></i> ${session.options_count || 0} opțiuni</span>
                    <span><i class="fas fa-calendar"></i> ${this.formatDate(session.created_at)}</span>
                    ${session.data_inceput ? `<span><i class="fas fa-play"></i> Start: ${this.formatDateTime(session.data_inceput)}</span>` : ''}
                    ${session.data_sfarsit ? `<span><i class="fas fa-stop"></i> End: ${this.formatDateTime(session.data_sfarsit)}</span>` : ''}
                </div>
                <div class="item-actions">
                    <button class="btn-small btn-primary" data-action="edit-session" data-id="${session.id}" title="Editează sesiunea">
                        <i class="fas fa-edit"></i> Editează
                    </button>
                    <button class="btn-small btn-secondary" data-action="view-results" data-id="${session.id}" title="Vezi rezultate">
                        <i class="fas fa-chart-bar"></i> Rezultate
                    </button>
                    <button class="btn-small btn-danger" data-action="delete-session" data-id="${session.id}" title="Șterge sesiunea">
                        <i class="fas fa-trash"></i> Șterge
                    </button>
                </div>
            </div>
        `).join('');
    }

    openSessionModal(sessionId = null) {
        const modal = document.getElementById('sessionModal');
        const form = document.getElementById('sessionForm');
        const title = document.getElementById('sessionModalTitle');
        
        form.reset();
        document.getElementById('sessionId').value = sessionId || '';
        
        if (sessionId) {
            title.innerHTML = '<i class="fas fa-edit"></i> Editează Sesiune';
            this.loadSessionData(sessionId);
        } else {
            title.innerHTML = '<i class="fas fa-plus"></i> Crează Sesiune Nouă';
        }
        
        modal.style.display = 'flex';
    }

    async loadSessionData(sessionId) {
        try {
            const sessionsResponse = await fetch(`${this.apiBaseUrl}/admin/sessions`);
            if (sessionsResponse.ok) {
                const sessions = await sessionsResponse.json();
                const session = sessions.find(s => s.id === sessionId);
                if (session) {
                    document.getElementById('sessionTitle').value = session.titlu || '';
                    document.getElementById('sessionDescription').value = session.descriere || '';
                    document.getElementById('sessionStatus').value = session.status || 'active';
                    
                    // Format dates for datetime-local input
                    // MySQL returnează date în format 'YYYY-MM-DD HH:MM:SS' fără fus orar
                    // Trebuie să le tratăm ca fiind în fusul orar local
                    if (session.data_inceput) {
                        // Înlocuiește spațiul cu T pentru a crea un format ISO valid
                        const dateStr = session.data_inceput.replace(' ', 'T');
                        const startDate = new Date(dateStr);
                        if (!isNaN(startDate.getTime())) {
                            document.getElementById('sessionDateStart').value = this.formatDateTimeLocal(startDate);
                        }
                    }
                    if (session.data_sfarsit) {
                        // Înlocuiește spațiul cu T pentru a crea un format ISO valid
                        const dateStr = session.data_sfarsit.replace(' ', 'T');
                        const endDate = new Date(dateStr);
                        if (!isNaN(endDate.getTime())) {
                            document.getElementById('sessionDateEnd').value = this.formatDateTimeLocal(endDate);
                        }
                    }
                    
                    // Load options
                    const optionsResponse = await fetch(`${this.apiBaseUrl}/sessions/${sessionId}/options`);
                    if (optionsResponse.ok) {
                        const options = await optionsResponse.json();
                        document.getElementById('sessionOptions').value = options.map(o => o.text_optiune).join('\n');
                    }
                }
            }
        } catch (error) {
            console.error('Eroare la încărcarea datelor sesiunii:', error);
        }
    }

    async saveSession() {
        const sessionId = document.getElementById('sessionId').value;
        const title = document.getElementById('sessionTitle').value;
        const description = document.getElementById('sessionDescription').value;
        const status = document.getElementById('sessionStatus').value;
        const dateStart = document.getElementById('sessionDateStart').value;
        const dateEnd = document.getElementById('sessionDateEnd').value;
        const optionsText = document.getElementById('sessionOptions').value;
        
        const options = optionsText.split('\n').filter(opt => opt.trim()).map(opt => opt.trim());

        if (!title || options.length < 2) {
            this.showToast('Completează titlul și cel puțin 2 opțiuni', 'error');
            return;
        }

        // Validare date
        if (dateStart && dateEnd) {
            const start = new Date(dateStart);
            const end = new Date(dateEnd);
            if (end <= start) {
                this.showToast('Data de sfârșit trebuie să fie după data de început', 'error');
                return;
            }
        }

        try {
            const url = sessionId 
                ? `${this.apiBaseUrl}/admin/sessions/${sessionId}`
                : `${this.apiBaseUrl}/admin/sessions`;
            const method = sessionId ? 'PUT' : 'POST';

            const body = {
                titlu: title,
                descriere: description,
                status: status,
                options: options
            };

            // Adaugă date doar dacă sunt completate (format MySQL: YYYY-MM-DD HH:MM:SS)
            // datetime-local returnează format YYYY-MM-DDTHH:mm în fusul orar local
            if (dateStart) {
                // datetime-local returnează deja formatul corect, doar înlocuim T cu spațiu
                body.data_inceput = dateStart.replace('T', ' ') + ':00';
            }
            if (dateEnd) {
                // datetime-local returnează deja formatul corect, doar înlocuim T cu spațiu
                body.data_sfarsit = dateEnd.replace('T', ' ') + ':00';
            }

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            const result = await response.json();

            if (response.ok) {
                this.showToast(sessionId ? 'Sesiune actualizată cu succes!' : 'Sesiune creată cu succes!', 'success');
                this.closeSessionModal();
                await this.loadSessions();
                await this.loadStats();
            } else {
                throw new Error(result.error || 'Eroare la salvarea sesiunii');
            }
        } catch (error) {
            console.error('❌ Eroare:', error);
            this.showToast(error.message, 'error');
        }
    }

    async deleteSession(sessionId) {
        if (!confirm('Sigur doriți să ștergeți această sesiune? Această acțiune nu poate fi anulată.')) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/sessions/${sessionId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Sesiune ștearsă cu succes!', 'success');
                await this.loadSessions();
                await this.loadStats();
            } else {
                throw new Error('Eroare la ștergerea sesiunii');
            }
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    editSession(sessionId) {
        this.openSessionModal(sessionId);
    }

    async viewSessionResults(sessionId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/sessions/${sessionId}/results`);
            if (response.ok) {
                const data = await response.json();
                alert(`Rezultate pentru "${data.session_title}":\n\n` +
                    data.results.map(r => `${r.option}: ${r.votes} voturi (${r.percentage}%)`).join('\n') +
                    `\n\nTotal voturi: ${data.total_votes}`);
            }
        } catch (error) {
            this.showToast('Eroare la încărcarea rezultatelor', 'error');
        }
    }

    closeSessionModal() {
        document.getElementById('sessionModal').style.display = 'none';
        document.getElementById('sessionForm').reset();
    }

    // ===== NOUTĂȚI =====
    async loadNews() {
        const container = document.getElementById('newsList');
        if (!container) return;

        container.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Se încarcă noutățile...</p></div>';

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/news`);
            if (response.ok) {
                const news = await response.json();
                this.displayNews(news);
            } else {
                container.innerHTML = '<div class="empty-state">Eroare la încărcarea noutăților</div>';
            }
        } catch (error) {
            console.error('❌ Eroare noutăți:', error);
            container.innerHTML = '<div class="empty-state">Eroare la încărcarea noutăților</div>';
        }
    }

    displayNews(news) {
        const container = document.getElementById('newsList');
        if (!news || news.length === 0) {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><p>Nu există noutăți.</p></div>';
            this.updateBadge('newsBadge', 0);
            return;
        }

        this.updateBadge('newsBadge', news.length);

        container.innerHTML = news.map(item => `
            <div class="item-card">
                <div class="item-header">
                    <h3>${this.escapeHtml(item.titlu)}</h3>
                    <span class="badge ${item.status}">${item.status || 'active'}</span>
                </div>
                ${item.continut ? `<p class="item-description">${this.escapeHtml(item.continut.substring(0, 150))}${item.continut.length > 150 ? '...' : ''}</p>` : ''}
                <div class="item-meta">
                    <span><i class="fas fa-user"></i> ${item.autor || 'Administrator'}</span>
                    <span><i class="fas fa-calendar"></i> ${this.formatDate(item.data_publicarii)}</span>
                </div>
                <div class="item-actions">
                    <button class="btn-small btn-primary" data-action="edit-news" data-id="${item.id}" title="Editează noutatea">
                        <i class="fas fa-edit"></i> Editează
                    </button>
                    <button class="btn-small btn-danger" data-action="delete-news" data-id="${item.id}" title="Șterge noutatea">
                        <i class="fas fa-trash"></i> Șterge
                    </button>
                </div>
            </div>
        `).join('');
    }

    openNewsModal(newsId = null) {
        const modal = document.getElementById('newsModal');
        const form = document.getElementById('newsForm');
        const title = document.getElementById('newsModalTitle');
        
        form.reset();
        document.getElementById('newsId').value = newsId || '';
        
        if (newsId) {
            title.innerHTML = '<i class="fas fa-edit"></i> Editează Noutate';
            this.loadNewsData(newsId);
        } else {
            title.innerHTML = '<i class="fas fa-plus"></i> Adaugă Noutate';
        }
        
        modal.style.display = 'flex';
    }

    async loadNewsData(newsId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/news`);
            if (response.ok) {
                const news = await response.json();
                const item = news.find(n => n.id === newsId);
                if (item) {
                    document.getElementById('newsTitle').value = item.titlu || '';
                    document.getElementById('newsContent').value = item.continut || '';
                    document.getElementById('newsAuthor').value = item.autor || 'Administrator';
                    document.getElementById('newsStatus').value = item.status || 'active';
                }
            }
        } catch (error) {
            console.error('Eroare la încărcarea datelor noutății:', error);
        }
    }

    async saveNews() {
        const newsId = document.getElementById('newsId').value;
        const title = document.getElementById('newsTitle').value;
        const content = document.getElementById('newsContent').value;
        const author = document.getElementById('newsAuthor').value;
        const status = document.getElementById('newsStatus').value;

        if (!title) {
            this.showToast('Titlul este obligatoriu', 'error');
            return;
        }

        try {
            const url = newsId 
                ? `${this.apiBaseUrl}/admin/news/${newsId}`
                : `${this.apiBaseUrl}/admin/news`;
            const method = newsId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    titlu: title,
                    continut: content,
                    autor: author,
                    status: status
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showToast(newsId ? 'Noutate actualizată cu succes!' : 'Noutate creată cu succes!', 'success');
                this.closeNewsModal();
                await this.loadNews();
                await this.loadStats(); // Actualizează statisticile
            } else {
                throw new Error(result.error || 'Eroare la salvarea noutății');
            }
        } catch (error) {
            console.error('❌ Eroare:', error);
            this.showToast(error.message, 'error');
        }
    }

    async deleteNews(newsId) {
        if (!confirm('Sigur doriți să ștergeți această noutate?')) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/news/${newsId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Noutate ștearsă cu succes!', 'success');
                await this.loadNews();
                await this.loadStats(); // Actualizează statisticile
            } else {
                throw new Error('Eroare la ștergerea noutății');
            }
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    editNews(newsId) {
        this.openNewsModal(newsId);
    }

    closeNewsModal() {
        document.getElementById('newsModal').style.display = 'none';
        document.getElementById('newsForm').reset();
    }

    // ===== REZULTATE =====
    async loadResults() {
        const container = document.getElementById('resultsList');
        if (!container) return;

        container.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Se încarcă rezultatele...</p></div>';

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/results`);
            if (response.ok) {
                const results = await response.json();
                this.displayResults(results);
            } else {
                container.innerHTML = '<div class="empty-state">Eroare la încărcarea rezultatelor</div>';
            }
        } catch (error) {
            console.error('❌ Eroare rezultate:', error);
            container.innerHTML = '<div class="empty-state">Eroare la încărcarea rezultatelor</div>';
        }
    }

    displayResults(results) {
        const container = document.getElementById('resultsList');
        if (!results || results.length === 0) {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><p>Nu există rezultate.</p></div>';
            this.updateBadge('resultsBadge', 0);
            return;
        }

        this.updateBadge('resultsBadge', results.length);

        container.innerHTML = results.map(item => `
            <div class="item-card">
                <div class="item-header">
                    <h3>${this.escapeHtml(item.titlu)}</h3>
                </div>
                ${item.descriere ? `<p class="item-description">${this.escapeHtml(item.descriere)}</p>` : ''}
                <div class="item-meta">
                    ${item.session_titlu ? `<span><i class="fas fa-vote-yea"></i> ${this.escapeHtml(item.session_titlu)}</span>` : ''}
                    <span><i class="fas fa-poll"></i> ${item.total_voturi || 0} voturi</span>
                    ${item.castigator ? `<span><i class="fas fa-trophy"></i> ${this.escapeHtml(item.castigator)}</span>` : ''}
                    <span><i class="fas fa-calendar"></i> ${this.formatDate(item.data_publicarii)}</span>
                </div>
                <div class="item-actions">
                    <button class="btn-small btn-primary" data-action="edit-result" data-id="${item.id}" title="Editează rezultatul">
                        <i class="fas fa-edit"></i> Editează
                    </button>
                    <button class="btn-small btn-danger" data-action="delete-result" data-id="${item.id}" title="Șterge rezultatul">
                        <i class="fas fa-trash"></i> Șterge
                    </button>
                </div>
            </div>
        `).join('');
    }

    async openResultModal(resultId = null) {
        const modal = document.getElementById('resultModal');
        const form = document.getElementById('resultForm');
        const title = document.getElementById('resultModalTitle');
        
        form.reset();
        document.getElementById('resultId').value = resultId || '';
        
        // Load sessions for dropdown
        await this.loadSessionsForDropdown();
        
        if (resultId) {
            title.innerHTML = '<i class="fas fa-edit"></i> Editează Rezultat';
            await this.loadResultData(resultId);
        } else {
            title.innerHTML = '<i class="fas fa-plus"></i> Adaugă Rezultat';
        }
        
        modal.style.display = 'flex';
    }

    async loadSessionsForDropdown() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/sessions`);
            if (response.ok) {
                const sessions = await response.json();
                const select = document.getElementById('resultSessionId');
                select.innerHTML = '<option value="">Selectează sesiune</option>' +
                    sessions.map(s => `<option value="${s.id}">${this.escapeHtml(s.titlu)}</option>`).join('');
            }
        } catch (error) {
            console.error('Eroare la încărcarea sesiunilor:', error);
        }
    }

    async loadResultData(resultId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/results`);
            if (response.ok) {
                const results = await response.json();
                const item = results.find(r => r.id === resultId);
                if (item) {
                    document.getElementById('resultTitle').value = item.titlu || '';
                    document.getElementById('resultDescription').value = item.descriere || '';
                    document.getElementById('resultSessionId').value = item.id_sesiune || '';
                    document.getElementById('resultTotalVotes').value = item.total_voturi || 0;
                    document.getElementById('resultWinner').value = item.castigator || '';
                }
            }
        } catch (error) {
            console.error('Eroare la încărcarea datelor rezultatului:', error);
        }
    }

    async saveResult() {
        const resultId = document.getElementById('resultId').value;
        const title = document.getElementById('resultTitle').value.trim();
        const description = document.getElementById('resultDescription').value.trim();
        const sessionId = document.getElementById('resultSessionId').value;
        const totalVotes = parseInt(document.getElementById('resultTotalVotes').value) || 0;
        const winner = document.getElementById('resultWinner').value.trim();

        if (!title) {
            this.showToast('Titlul este obligatoriu', 'error');
            return;
        }

        try {
            const url = resultId 
                ? `${this.apiBaseUrl}/admin/results/${resultId}`
                : `${this.apiBaseUrl}/admin/results`;
            const method = resultId ? 'PUT' : 'POST';

            // Pregătește datele pentru trimitere
            const data = {
                titlu: title,
                descriere: description || '',
                total_voturi: totalVotes,
                castigator: winner || ''
            };

            // Adaugă id_sesiune doar dacă este selectat (nu string gol)
            if (sessionId && sessionId !== '') {
                data.id_sesiune = parseInt(sessionId);
            } else {
                data.id_sesiune = null;
            }

            console.log('📤 Trimite date rezultat:', data);

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            console.log('📥 Răspuns server:', result);

            if (response.ok) {
                this.showToast(resultId ? 'Rezultat actualizat cu succes!' : 'Rezultat creat cu succes!', 'success');
                this.closeResultModal();
                await this.loadResults();
                await this.loadStats(); // Actualizează statisticile
            } else {
                throw new Error(result.error || 'Eroare la salvarea rezultatului');
            }
        } catch (error) {
            console.error('❌ Eroare:', error);
            this.showToast(error.message, 'error');
        }
    }

    async deleteResult(resultId) {
        if (!confirm('Sigur doriți să ștergeți acest rezultat?')) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/results/${resultId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Rezultat șters cu succes!', 'success');
                await this.loadResults();
                await this.loadStats(); // Actualizează statisticile
            } else {
                throw new Error('Eroare la ștergerea rezultatului');
            }
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    editResult(resultId) {
        this.openResultModal(resultId);
    }

    closeResultModal() {
        document.getElementById('resultModal').style.display = 'none';
        document.getElementById('resultForm').reset();
    }

    // ===== UTILIZATORI =====
    async loadUsers() {
        const container = document.getElementById('usersList');
        if (!container) return;

        container.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Se încarcă utilizatorii...</p></div>';

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/users`);
            if (response.ok) {
                const users = await response.json();
                this.displayUsers(users);
            } else {
                container.innerHTML = '<div class="empty-state">Eroare la încărcarea utilizatorilor</div>';
            }
        } catch (error) {
            console.error('❌ Eroare utilizatori:', error);
            container.innerHTML = '<div class="empty-state">Eroare la încărcarea utilizatorilor</div>';
        }
    }

    displayUsers(users) {
        const container = document.getElementById('usersList');
        if (!users || users.length === 0) {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><p>Nu există utilizatori.</p></div>';
            this.updateBadge('usersBadge', 0);
            return;
        }

        this.updateBadge('usersBadge', users.length);

        container.innerHTML = users.map(user => `
            <div class="item-card">
                <div class="item-header">
                    <h3>${this.escapeHtml(user.nume)}</h3>
                    <span class="badge ${user.is_admin ? 'admin' : 'user'}">${user.is_admin ? 'ADMIN' : 'USER'}</span>
                </div>
                <div class="item-meta">
                    <span><i class="fas fa-id-card"></i> IDNP: ${user.idnp}</span>
                    ${user.email ? `<span><i class="fas fa-envelope"></i> ${this.escapeHtml(user.email)}</span>` : ''}
                    ${user.telefon ? `<span><i class="fas fa-phone"></i> ${user.telefon}</span>` : ''}
                    <span><i class="fas fa-calendar"></i> ${this.formatDate(user.data_inregistrare)}</span>
                </div>
                ${!user.is_admin ? `
                    <div class="item-actions">
                        <button class="btn-small btn-danger" data-action="delete-user" data-id="${user.id}" title="Șterge utilizatorul">
                            <i class="fas fa-trash"></i> Șterge
                        </button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    async deleteUser(userId) {
        if (!confirm('Sigur doriți să ștergeți acest utilizator?')) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/users/${userId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Utilizator șters cu succes!', 'success');
                await this.loadUsers();
                await this.loadStats();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Eroare la ștergerea utilizatorului');
            }
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    // ===== UTILITARE =====
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

        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            // Verifică dacă data este validă (nu este epoch 0 sau invalidă)
            if (isNaN(date.getTime()) || date.getTime() <= 0) {
                return 'Data invalidă';
            }
            return date.toLocaleDateString('ro-RO', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (e) {
            console.error('Eroare la formatarea datei:', e, dateString);
            return 'Data invalidă';
        }
    }

    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('ro-RO', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatDateTimeLocal(date) {
        if (!date) return '';
        const d = new Date(date);
        
        // Verifică dacă data este validă
        if (isNaN(d.getTime())) {
            console.error('Data invalidă:', date);
            return '';
        }
        
        // Folosește metodele locale pentru a evita problemele cu fusul orar
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        
        // Format pentru datetime-local: YYYY-MM-DDTHH:mm
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    }

    updateBadge(badgeId, count) {
        const badge = document.getElementById(badgeId);
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }
}

// Initializează panoul admin
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM loaded, initializing admin panel...');
    window.adminPanel = new AdminPanel();
});

