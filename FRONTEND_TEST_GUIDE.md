# 🎨 Ghid Testare Frontend - AI Chat

## ✅ Tot ce e gata:

### Backend:
- ✅ API AI Chat funcționează (`/api/v1/ai-chat/query`)
- ✅ GPT-4o-mini configurat (folosește din $9.90)
- ✅ Toate serviciile funcționale (orders, inventory, tasks, crops)
- ✅ MongoDB cu date test

### Frontend:
- ✅ `AIChat.tsx` component creat
- ✅ `AIChatDemo.tsx` pagină completă
- ✅ Route adăugat în `App.tsx` (`/ai-chat`)
- ✅ Link în navigație (sidebar): **AI Chat** 💬
- ✅ Voice Input (🎤) + Text-to-Speech (🔊)

---

## 🚀 Pornire Frontend:

### Pasul 1: Navighează în Frontend
```bash
cd Frontend
```

### Pasul 2: Instalează dependințe (dacă nu ai făcut deja)
```bash
npm install
```

### Pasul 3: Pornește dev server
```bash
npm run dev
```

**Frontend va porni pe:** `http://localhost:5173`

---

## 🧪 Cum să testezi:

### 1. **Deschide Browser**
```
http://localhost:5173
```

### 2. **Click pe "AI Chat" în Sidebar**
- Sidebar-ul din stânga
- Iconița 💬 MessageCircle
- Label: **"AI Chat"**

### 3. **Testează Chat**

**Întrebări Simple:**
- "ce comenzi am astazi?"
- "cat valorează inventarul?"
- "ce task-uri am?"

**Întrebări Complexe:**
- "ce comenzi am astazi si cat valorează?"
- "cat valorează inventarul meu si ce task-uri am de făcut?"
- "da-mi un rezumat complet al fermei"

**Cu Context:**
```
Tu: "ce comenzi am?"
AI: "Ai 1 comandă..."

Tu: "și cât valorează?"
AI: "250 RON"
```

### 4. **Testează Voice Input** 🎤

1. Click pe butonul microfon (🎤)
2. Browser cere permisiune → Permite
3. Vorbește în română: "ce comenzi am astazi?"
4. Text apare automat în input
5. Click "Trimite" sau Enter

**Browser Support:** Chrome sau Edge (recomandat)

### 5. **Ascultă Răspunsurile** 🔊

- Răspunsurile AI sunt citite automat
- Voce română naturală
- Control volum din browser

---

## 📱 Quick Suggestions

Click pe sugestiile rapide din josul chat-ului:
- "Ce comenzi am astăzi?"
- "Cât am vândut luna asta?"
- "Ce task-uri am?"
- "Spune-mi despre inventar"

---

## 🎨 Features UI:

### Header:
- **Title:** "🤖 Asistent AI pentru Fermieri"
- **Subtitle:** "Ghidat de Gemini 2.5 Flash" (GPT-4o-mini acum)

### Chat:
- **Mesaje user:** Albastru (dreapta)
- **Mesaje AI:** Gri (stânga)
- **Avatar Bot:** 🤖 verde
- **Avatar User:** 👤 albastru

### Input Bar:
- **Text input** cu placeholder
- **Voice button** (🎤/🎙️)
- **Send button** (✈️)

### Bottom:
- **4 Quick suggestions** clickable
- **Data preview** (expandable pentru date structurate)

---

## 🐛 Troubleshooting:

### Frontend nu pornește:
```bash
# Reinstalează dependințe
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### "AI Chat" nu apare în sidebar:
- ✅ Verifică că ai salvat `Layout.tsx`
- ✅ Refresh browser (Cmd/Ctrl + R)
- ✅ Hard refresh (Cmd/Ctrl + Shift + R)

### Chat dă eroare:
- ✅ Verifică că backend rulează pe :8000
- ✅ Test backend direct:
  ```bash
  curl -X POST http://localhost:8000/api/v1/ai-chat/query \
    -H "Content-Type: application/json" \
    -d '{"farmer_id":"6917d631cc91724e7c5d0312","message":"salut"}'
  ```

### Voice Input nu funcționează:
- ✅ Folosește Chrome sau Edge
- ✅ Permite permisiuni microfon
- ✅ Verifică setări browser pentru microfon

### CORS errors:
- ✅ Backend CORS deja configurat pentru localhost:5173
- ✅ Verifică că backend rulează
- ✅ Verifică console browser pentru erori

---

## 📊 Date Test Disponibile:

**Farmer ID:** `6917d631cc91724e7c5d0312`

**Ce date există:**
- ✅ **Comenzi:** 1 comandă (250 RON)
- ✅ **Inventar:** 3 produse (1,995 RON valoare)
- ✅ **Tasks:** 1 astăzi, 1 întârziat
- ✅ **Culturi:** 4 culturi plantate

---

## 🎯 Răspunsuri Așteptate:

### "ce comenzi am astazi?"
```
"Ai o singură comandă astăzi, cu un venit total de 250.0 RON."
```

### "cat valorează inventarul meu?"
```
"Valoarea inventarului tău este de 1995.0 RON."
```

### "da-mi un rezumat complet"
```
- Venit total: 250.0 RON
- Valoare inventar: 1995.0 RON
- Produse în stoc: 3
- Culturi: 4
- Task-uri astăzi: 1
- Task-uri întârziate: 1
```

---

## ✅ Checklist Final:

- [ ] Frontend pornește pe :5173
- [ ] Backend pornește pe :8000
- [ ] "AI Chat" apare în sidebar
- [ ] Click pe "AI Chat" deschide pagina
- [ ] Chat UI se încarcă frumos
- [ ] Quick suggestions sunt clickabile
- [ ] Pot scrie mesaj și trimite
- [ ] AI răspunde corect cu date reale
- [ ] Voice input funcționează (Chrome/Edge)
- [ ] Text-to-speech citește răspunsuri
- [ ] Data preview se expandează când dai click

---

## 🎉 Success Indicators:

### ✅ Totul funcționează când:
1. Vezi pagina AI Chat frumoasă (gradient verde-albastru)
2. AI răspunde la întrebări cu date reale
3. Numerele din răspunsuri corespund cu datele test
4. Voice input transcrie corect în română
5. Răspunsurile sunt citite cu voce

---

## 📸 Screenshots Locations:

Chat va arăta ca:
```
┌─────────────────────────────────────┐
│ 🤖 Asistent AI pentru Fermieri     │
│ Ghidat de Gemini 2.5 Flash         │
├─────────────────────────────────────┤
│                                     │
│ [Bot] Bună! Sunt asistentul...     │
│                                     │
│         [User] ce comenzi am? 👤    │
│                                     │
│ [Bot] Ai o singură comandă...  🤖  │
│                                     │
├─────────────────────────────────────┤
│ [Input] [🎤] [Trimite ✈️]          │
│                                     │
│ Quick: [Ce comenzi am astăzi?]     │
└─────────────────────────────────────┘
```

---

**🚀 GATA DE TESTARE!**

Navighează la sidebar → Click "AI Chat" → Start chatting! 💬
