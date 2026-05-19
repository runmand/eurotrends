# 🐍 BACKEND - API Python com Google Trends

Esta pasta contém o **BACKEND** que busca dados reais do Google Trends.

---

## 📦 O QUE TEM AQUI:

```
BACKEND/
├── app.py              ← Código principal da API
├── requirements.txt    ← Bibliotecas Python necessárias
├── Dockerfile         ← Para deploy com Docker
├── railway.toml       ← Configuração Railway
├── test.py           ← Script de teste
└── README.md         ← Este arquivo
```

---

## 🚀 DEPLOY NO RAILWAY (Passo a Passo)

### **PASSO 1: GitHub**

```bash
cd BACKEND

git init
git add .
git commit -m "Backend inicial"

# Crie repo VAZIO no GitHub chamado "euro-trends-backend"
# Depois:

git remote add origin https://github.com/SEU-USUARIO/euro-trends-backend.git
git branch -M main
git push -u origin main
```

### **PASSO 2: Railway**

1. Acesse: https://railway.app
2. Login com GitHub
3. **New Project**
4. **Deploy from GitHub repo**
5. Selecione: `euro-trends-backend`
6. **Root Directory:** DEIXE VAZIO
7. Clique **Deploy**
8. Aguarde 3-5 minutos

### **PASSO 3: Pegar URL**

1. Vá em **Settings**
2. Seção **Networking**
3. Clique **Generate Domain**
4. **COPIE A URL:**
   ```
   https://euro-trends-backend-xxx.up.railway.app
   ```

### **PASSO 4: Testar**

Abra no navegador:
```
https://SEU-BACKEND.up.railway.app/api/health
```

Deve ver:
```json
{"status": "healthy", "countries": 10}
```

✅ **BACKEND FUNCIONANDO!**

---

## 📡 ENDPOINTS DA API

### Health Check
```
GET /api/health
```

### Todos os Trends
```
GET /api/trends
```

### Force Refresh
```
POST /api/trends/refresh
```

---

## 💡 GUARDE ESTA URL!

Você vai precisar dela no FRONTEND:
```
https://euro-trends-backend-xxx.up.railway.app
```

---

## 🧪 Testar Localmente (Opcional)

```bash
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000/api/health

---

## ✅ CHECKLIST

```
✅ GitHub: repo criado
✅ Railway: deploy feito
✅ Domain: URL copiada
✅ Teste: /api/health OK
```

**Próximo: Deploy FRONTEND!** →
