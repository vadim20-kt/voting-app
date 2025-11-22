-- ============================================
-- FIXARE DATA PUBLICARII PENTRU NOUTATI
-- ============================================

-- Verifică structura tabelei
DESCRIBE noutati;

-- Verifică noutățile cu data NULL sau invalidă
SELECT id, titlu, data_publicarii, autor 
FROM noutati 
WHERE data_publicarii IS NULL 
   OR data_publicarii = '1970-01-01 00:00:00'
   OR data_publicarii = '0000-00-00 00:00:00'
ORDER BY id DESC;

-- Actualizează data_publicarii pentru noutățile cu data NULL sau invalidă
-- Folosește data curentă sau data creării (dacă există)
UPDATE noutati 
SET data_publicarii = NOW()
WHERE data_publicarii IS NULL 
   OR data_publicarii = '1970-01-01 00:00:00'
   OR data_publicarii = '0000-00-00 00:00:00';

-- Verifică rezultatul
SELECT id, titlu, data_publicarii, autor 
FROM noutati 
ORDER BY data_publicarii DESC 
LIMIT 10;

