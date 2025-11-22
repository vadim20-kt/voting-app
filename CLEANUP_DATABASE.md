# Ghid pentru Curățarea Bazei de Date

## Tabele care TREBUIE PĂSTRATE (folosite în aplicație):

### ✅ Tabele Active:
1. **users** - Utilizatori (folosit în toate rutele)
2. **voting_sessions** - Sesiuni de vot (folosit în toate rutele)
3. **vote_options** - Opțiuni de vot (folosit în toate rutele)
4. **votes** - Voturi (folosit în toate rutele)
5. **noutati** - Noutăți (folosit în rutele admin și user)
6. **rezultate** - Rezultate (folosit în rutele admin și user)
7. **login_logs** - Loguri de login (folosit în auth_routes.py)
8. **verification_codes** - Coduri de verificare (folosit în auth_routes.py)

## ❌ Tabele care TREBUIE ȘTERSE (duplicate/neutilizate):

### Tabele Duplicate/Neutilizate:
1. **utilizatori** - DUPLICAT al tabelei `users`
   - ❌ ȘTERGE: `DROP TABLE IF EXISTS utilizatori;`
   - ✅ Folosește: `users`

2. **sesiuni** - DUPLICAT al tabelei `voting_sessions`
   - ❌ ȘTERGE: `DROP TABLE IF EXISTS sesiuni;`
   - ✅ Folosește: `voting_sessions`

3. **optiuni** - DUPLICAT al tabelei `vote_options`
   - ❌ ȘTERGE: `DROP TABLE IF EXISTS optiuni;`
   - ✅ Folosește: `vote_options`

4. **voturi** - DUPLICAT al tabelei `votes`
   - ❌ ȘTERGE: `DROP TABLE IF EXISTS voturi;`
   - ✅ Folosește: `votes`

5. **Новая** - Tabel necunoscut/neutilizat
   - ❌ ȘTERGE: `DROP TABLE IF EXISTS Новая;`

## Comenzi SQL pentru Curățare:

**Folosește fișierul `CLEANUP_DATABASE.sql` pentru a rula toate comenzile automat!**

Sau rulează manual:

```sql
-- Șterge tabelele duplicate/neutilizate
DROP TABLE IF EXISTS utilizatori;
DROP TABLE IF EXISTS sesiuni;
DROP TABLE IF EXISTS optiuni;
DROP TABLE IF EXISTS voturi;
DROP TABLE IF EXISTS Новая;

-- Adaugă coloana 'autor' în tabela noutati dacă nu există
ALTER TABLE noutati 
ADD COLUMN IF NOT EXISTS autor VARCHAR(100) AFTER continut;

-- Adaugă coloana 'status' în tabela noutati dacă nu există
ALTER TABLE noutati 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' AFTER autor;
```

## Structura Finală a Bazei de Date:

După curățare, baza de date `voting_app` va conține doar:

1. ✅ **users** - Utilizatori
2. ✅ **voting_sessions** - Sesiuni de vot
3. ✅ **vote_options** - Opțiuni de vot
4. ✅ **votes** - Voturi
5. ✅ **noutati** - Noutăți
6. ✅ **rezultate** - Rezultate
7. ✅ **login_logs** - Loguri de login
8. ✅ **verification_codes** - Coduri de verificare

## Notă Importantă:

**ÎNAINTE DE ȘTERGERE**, verifică dacă există date importante în tabelele duplicate:
- Dacă ai date în `utilizatori`, `sesiuni`, `optiuni`, `voturi` care nu sunt în tabelele principale, migrează-le mai întâi!

