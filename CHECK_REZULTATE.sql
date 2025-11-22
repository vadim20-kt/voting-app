-- ============================================
-- VERIFICARE STRUCTURĂ TABELĂ REZULTATE
-- ============================================

-- Verifică dacă tabela rezultate există și structura ei
DESCRIBE rezultate;

-- Verifică dacă există date în tabela rezultate
SELECT COUNT(*) as total_rezultate FROM rezultate;

-- Afișează ultimele 5 rezultate
SELECT * FROM rezultate ORDER BY id DESC LIMIT 5;

-- Verifică sesiunile disponibile
SELECT id, titlu, status FROM voting_sessions ORDER BY id DESC;

-- Verifică foreign key constraints pentru rezultate
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

