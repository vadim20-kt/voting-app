-- ============================================
-- SCRIPT PENTRU ACTUALIZAREA STATUSULUI SESIUNILOR
-- ============================================
-- Rulează acest script periodic sau manual pentru a actualiza statusul sesiunilor

-- Marchează sesiunile expirate ca "completed"
UPDATE voting_sessions 
SET status = 'completed' 
WHERE status = 'active' 
AND data_sfarsit IS NOT NULL 
AND data_sfarsit < NOW();

-- Marchează sesiunile care nu au început încă ca "pending"
UPDATE voting_sessions 
SET status = 'pending' 
WHERE status = 'active' 
AND data_inceput IS NOT NULL 
AND data_inceput > NOW();

-- Activează sesiunile care au început dar sunt marcate ca "pending"
UPDATE voting_sessions 
SET status = 'active' 
WHERE status = 'pending' 
AND data_inceput IS NOT NULL 
AND data_inceput <= NOW()
AND (data_sfarsit IS NULL OR data_sfarsit >= NOW());

-- Verifică rezultatul
SELECT 
    id, 
    titlu, 
    status, 
    data_inceput, 
    data_sfarsit,
    CASE 
        WHEN data_sfarsit IS NOT NULL AND data_sfarsit < NOW() THEN 'EXPIRAT'
        WHEN data_inceput IS NOT NULL AND data_inceput > NOW() THEN 'NU A ÎNCEPUT'
        WHEN data_inceput IS NOT NULL AND data_inceput <= NOW() AND (data_sfarsit IS NULL OR data_sfarsit >= NOW()) THEN 'ACTIV'
        ELSE 'FĂRĂ DATĂ'
    END as status_real
FROM voting_sessions
ORDER BY created_at DESC;

