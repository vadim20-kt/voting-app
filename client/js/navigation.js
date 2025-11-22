// Navigation helper - Gestionare navigare între pagini fără logout
class NavigationHelper {
    static init() {
        // Verifică dacă utilizatorul este autentificat
        this.checkAuthStatus();
        
        // Adaugă event listeners pentru navigare
        this.setupNavigation();
    }

    static checkAuthStatus() {
        const userData = localStorage.getItem('userData');
        if (!userData) return;

        try {
            const user = JSON.parse(userData);
            
            // Actualizează link-urile în funcție de rol
            if (user.is_admin) {
                this.showAdminLinks();
            } else {
                this.showUserLinks();
            }
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }

    static showAdminLinks() {
        // Pe pagina principală
        const authLinks = document.getElementById('authLinks');
        const adminLink = document.getElementById('adminLink');
        const logoutBtn = document.getElementById('logoutBtnMain');

        if (authLinks) authLinks.style.display = 'none';
        if (adminLink) adminLink.style.display = 'inline-block';
        if (logoutBtn) {
            logoutBtn.style.display = 'inline-flex';
            logoutBtn.onclick = () => {
                if (confirm('Sigur doriți să vă deconectați?')) {
                    AuthSystem.logout();
                }
            };
        }
    }

    static showUserLinks() {
        // Pe pagina principală
        const authLinks = document.getElementById('authLinks');
        const userLink = document.getElementById('userLink');
        const logoutBtn = document.getElementById('logoutBtnMain');

        if (authLinks) authLinks.style.display = 'none';
        if (userLink) userLink.style.display = 'inline-block';
        if (logoutBtn) {
            logoutBtn.style.display = 'inline-flex';
            logoutBtn.onclick = () => {
                if (confirm('Sigur doriți să vă deconectați?')) {
                    AuthSystem.logout();
                }
            };
        }
    }

    static setupNavigation() {
        // Previne refresh-ul la click pe link-uri către admin
        document.querySelectorAll('a[href*="admin"]').forEach(link => {
            link.addEventListener('click', (e) => {
                // Verifică dacă utilizatorul este admin
                const userData = localStorage.getItem('userData');
                if (userData) {
                    try {
                        const user = JSON.parse(userData);
                        if (!user.is_admin) {
                            e.preventDefault();
                            alert('Acces restricționat! Nu aveți drepturi de administrator.');
                            return false;
                        }
                    } catch (e) {
                        console.error('Error:', e);
                    }
                }
            });
        });
    }
}

// Inițializează navigarea
document.addEventListener('DOMContentLoaded', () => {
    NavigationHelper.init();
});

