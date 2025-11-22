-- ============================================
-- SCRIPT RAPID PENTRU FIXAREA TABELEI NOUTATI
-- ============================================
-- Rulează acest script dacă primești eroarea:
-- "Unknown column 'autor' in 'field list'"

-- Verifică și adaugă coloana 'autor' dacă lipsește
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
  'SELECT "Coloana autor există deja" as message',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(100) AFTER continut')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Verifică și adaugă coloana 'status' dacă lipsește
SET @columnname = 'status';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  'SELECT "Coloana status există deja" as message',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(20) DEFAULT ''active'' AFTER autor')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Verifică structura finală
DESCRIBE noutati;

