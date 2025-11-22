-- ============================================
-- SCRIPT PENTRU VERIFICAREA TABELEI REZULTATE
-- ============================================

-- Verifică structura tabelei rezultate
DESCRIBE rezultate;

-- Verifică dacă există date în tabela rezultate
SELECT * FROM rezultate ORDER BY id DESC LIMIT 10;

-- Verifică dacă există sesiuni disponibile
SELECT id, titlu, status FROM voting_sessions ORDER BY id DESC;

-- Verifică foreign key constraints
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'rezultate'
AND REFERENCED_TABLE_NAME IS NOT NULL;

