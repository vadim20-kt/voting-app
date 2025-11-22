// Funcții principale pentru pagina publică
class MainPage {
    constructor() {
        this.init();
    }

    init() {
        this.loadNews();
        this.loadResults();
        this.setupAnimations();
    }

    async loadNews() {
        try {
            const response = await fetch('/api/news');
            if (!response.ok) throw new Error('Network response was not ok');
            
            const news = await response.json();
            const newsContainer = document.getElementById('news-list');
            
            if (newsContainer && news.length > 0) {
                newsContainer.innerHTML = news.map(item => `
                    <div class="news-card">
                        <h3>${this.escapeHtml(item.titlu)}</h3>
                        <div class="date">${new Date(item.data_publicarii).toLocaleDateString('ro-RO')}</div>
                        <p>${this.escapeHtml(item.continut)}</p>
                    </div>
                `).join('');
            } else if (newsContainer) {
                newsContainer.innerHTML = '<p>Nu există știri momentan.</p>';
            }
        } catch (error) {
            console.error('Eroare la încărcarea noutăților:', error);
            const newsContainer = document.getElementById('news-list');
            if (newsContainer) {
                newsContainer.innerHTML = '<p>Eroare la încărcarea știrilor.</p>';
            }
        }
    }

    async loadResults() {
        try {
            const response = await fetch('/api/results');
            if (!response.ok) throw new Error('Network response was not ok');
            
            const results = await response.json();
            const resultsContainer = document.getElementById('results-list');
            
            if (resultsContainer && results.length > 0) {
                resultsContainer.innerHTML = results.map(item => `
                    <div class="news-card">
                        <h3>${this.escapeHtml(item.titlu)}</h3>
                        <p><strong>Total voturi:</strong> ${item.total_voturi}</p>
                        <p><strong>Câștigător:</strong> ${this.escapeHtml(item.castigator || 'Nedeterminat')}</p>
                    </div>
                `).join('');
            } else if (resultsContainer) {
                resultsContainer.innerHTML = '<p>Nu există rezultate momentan.</p>';
            }
        } catch (error) {
            console.error('Eroare la încărcarea rezultatelor:', error);
            const resultsContainer = document.getElementById('results-list');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<p>Eroare la încărcarea rezultatelor.</p>';
            }
        }
    }

    setupAnimations() {
        // Animații la scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        // Observează toate elementele cu clasa fade-in
        document.querySelectorAll('.fade-in').forEach(el => {
            observer.observe(el);
        });

        // Adaugă clasa fade-in dinamic elementelor din secțiuni
        document.querySelectorAll('.news-card, .regulation-card, .session-card').forEach(card => {
            card.classList.add('fade-in');
        });
    }

    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Check auth status for navigation
function checkAuthStatus() {
    const userData = localStorage.getItem('userData');
    const adminData = localStorage.getItem('adminData');
    const loginLink = document.getElementById('loginLink');
    const dashboardLink = document.getElementById('dashboardLink');

    if (loginLink && dashboardLink) {
        if (userData || adminData) {
            loginLink.style.display = 'none';
            dashboardLink.style.display = 'block';
        } else {
            loginLink.style.display = 'block';
            dashboardLink.style.display = 'none';
        }
    }
}

// Initialize main page
document.addEventListener('DOMContentLoaded', function() {
    new MainPage();
    checkAuthStatus();
});