-- ============================================
-- SCRIPT SQL PENTRU CURĂȚAREA BAZEI DE DATE
-- ============================================
-- Acest script șterge tabelele duplicate/neutilizate
-- și adaugă coloanele lipsă

-- ============================================
-- PARTEA 1: ȘTERGEREA TABELELOR DUPLICATE
-- ============================================

-- Șterge tabela utilizatori (duplicat al tabelei users)
DROP TABLE IF EXISTS utilizatori;

-- Șterge tabela sesiuni (duplicat al tabelei voting_sessions)
DROP TABLE IF EXISTS sesiuni;

-- Șterge tabela optiuni (duplicat al tabelei vote_options)
DROP TABLE IF EXISTS optiuni;

-- Șterge tabela voturi (duplicat al tabelei votes)
DROP TABLE IF EXISTS voturi;

-- Șterge tabela necunoscută
DROP TABLE IF EXISTS Новая;

-- ============================================
-- PARTEA 2: ADĂUGAREA COLOANELOR LIPSĂ
-- ============================================
-- NOTĂ: MySQL nu suportă "IF NOT EXISTS" pentru ALTER TABLE
-- Acest script verifică dacă coloanele există înainte de a le adăuga

-- Verifică și adaugă coloana 'autor' în tabela noutati
SET @dbname = DATABASE();
SET @tablename = 'noutati';
SET @columnname = 'autor';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(100) AFTER continut')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Verifică și adaugă coloana 'status' în tabela noutati
SET @columnname = 'status';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(20) DEFAULT ''active'' AFTER autor')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================
-- VERIFICARE FINALĂ
-- ============================================

-- Verifică structura tabelei noutati
DESCRIBE noutati;

-- Verifică structura tabelei rezultate
DESCRIBE rezultate;

-- Listează toate tabelele rămase
SHOW TABLES;

