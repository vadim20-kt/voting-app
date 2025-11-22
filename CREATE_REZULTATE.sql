-- ============================================
-- CREARE/VERIFICARE TABELĂ REZULTATE
-- ============================================

-- Verifică dacă tabela rezultate există
SHOW TABLES LIKE 'rezultate';

-- Dacă nu există, creează tabela rezultate
CREATE TABLE IF NOT EXISTS rezultate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_sesiune INT,
    titlu VARCHAR(255) NOT NULL,
    descriere TEXT,
    total_voturi INT DEFAULT 0,
    castigator VARCHAR(255),
    data_publicarii TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_sesiune) REFERENCES voting_sessions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verifică structura tabelei
DESCRIBE rezultate;

-- Verifică dacă există date
SELECT COUNT(*) as total FROM rezultate;

