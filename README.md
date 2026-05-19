# 🐍 BACKEND - Google Trends API

Backend Python que busca dados REAIS do Google Trends.

---

## 🚀 DEPLOY NO RAILWAY (5 PASSOS)

### **1. Subir para GitHub**

```bash
# VOCÊ JÁ DEVE ESTAR NESTA PASTA!
# Confirme com:
pwd
# Deve mostrar: .../BACKEND-PRONTO

# Inicializar Git
git init

# Adicionar arquivos
git add .

# Commit
git commit -m "Backend inicial"

# Criar repo VAZIO no GitHub chamado: euro-trends-backend

# Conectar
git remote add origin https://github.com/SEU-USUARIO/euro-trends-backend.git

# Enviar
git branch -M main
git push -u origin main
```

✅ **GitHub pronto!**

---

### **2. Railway - Novo Projeto**

1. Acesse: https://railway.app
2. Login com GitHub
3. **New Project**
4. **Deploy from GitHub repo**
5. Selecione: `euro-trends-backend`

---

### **3. Configurar**

**Root Directory:** DEIXE VAZIO (já está na raiz!)

**Start Command:** (Railway detecta automaticamente, mas se pedir)
```
gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app
```

---

### **4. Deploy**

Clique **Deploy**

Aguarde 3-5 minutos.

---

### **5. Pegar URL**

1. Settings → Networking
2. **Generate Domain**
3. Copie a URL:
   ```
   https://euro-trends-backend-production-xxx.up.railway.app
   ```

---

## ✅ TESTAR

Abra no navegador:
```
https://SUA-URL.up.railway.app/api/health
```

Deve retornar:
```json
{"status": "healthy", "countries": 10}
```

🎉 **FUNCIONOU!**

---

## 📡 ENDPOINTS

Sua API terá:

- `GET /api/health` - Health check
- `GET /api/trends` - Todos os trending products
- `POST /api/trends/refresh` - Force refresh

---

## 💾 GUARDE A URL!

Você vai precisar dela no FRONTEND!

Exemplo:
```
https://euro-trends-backend-production-abc123.up.railway.app
```

---

## 🐛 SE DER ERRO

**Veja os logs no Railway:**
1. Clique no projeto
2. Deployments
3. View Logs
4. Procure erros em vermelho

**Erros comuns:**
- "Module not found" → Railway instala automaticamente, aguarde
- "Timeout" → Normal na primeira request (30s)
- "Port in use" → Railway resolve automaticamente

---

## ✅ CHECKLIST

```
✅ Git init na pasta certa
✅ Push para GitHub
✅ Deploy no Railway
✅ Domain gerado
✅ /api/health funciona
```

**Próximo passo: Deploy FRONTEND!** →
