# 🚂 GLTREND V3 - GUIA DE DEPLOY NO RAILWAY

## 🎯 PASSO A PASSO COMPLETO

---

## 📦 PREPARAÇÃO (5 min)

### **1. Extrair o arquivo**

```bash
# Baixe GLTREND-INTELLIGENCE-V3.tar.gz
tar -xzf GLTREND-INTELLIGENCE-V3.tar.gz

# Entre na pasta
cd GLTREND-V3

# Veja o que tem
ls
# Deve mostrar:
# app.py
# requirements.txt
# railway.toml
# README.md
```

---

## 🐙 GITHUB (5 min)

### **Opção A: Atualizar repo existente**

```bash
# Se já tem um backend deployado

# Copie os novos arquivos
cp app.py SEU-REPO-BACKEND/
cp requirements.txt SEU-REPO-BACKEND/
cp railway.toml SEU-REPO-BACKEND/

# Entre no repo
cd SEU-REPO-BACKEND

# Commit
git add .
git commit -m "Upgrade to GLTREND Intelligence Platform V3"
git push

# Railway vai fazer redeploy automático! ✅
```

### **Opção B: Novo repositório**

```bash
# Na pasta GLTREND-V3

git init
git add .
git commit -m "GLTREND Intelligence Platform V3"

# Crie repo no GitHub: gltrend-backend

git remote add origin https://github.com/SEU-USUARIO/gltrend-backend.git
git branch -M main
git push -u origin main
```

---

## 🚂 RAILWAY DEPLOY (5 min)

### **Se está ATUALIZANDO backend existente:**

1. Railway vai detectar o push automaticamente
2. Aguarde 3-5 minutos
3. **PRONTO!** ✅

### **Se é NOVO projeto:**

1. Acesse: https://railway.app
2. **New Project**
3. **Deploy from GitHub repo**
4. Selecione: `gltrend-backend`
5. **Root Directory:** VAZIO
6. **NÃO adicione variáveis** (não precisa!)
7. Clique **Deploy**
8. Aguarde 3-5 minutos

---

## ⚙️ CONFIGURAÇÕES RAILWAY

### **Settings (verifique):**

```
Root Directory: (vazio)
Start Command: (vazio - railway.toml tem isso)
Build Command: (vazio - automático)
```

### **Variables (NENHUMA necessária!):**

O GLTREND V3 funciona sem variáveis de ambiente!

Tudo está hardcoded no código.

---

## 🌐 PEGAR URL

1. Quando deploy terminar (verde ✅)
2. **Settings** → **Networking**
3. **Generate Domain**
4. Copie a URL:
   ```
   https://gltrend-backend-production-xxx.up.railway.app
   ```

---

## 🧪 TESTAR

### **1. Health Check**

```bash
https://SUA-URL.up.railway.app/api/health
```

**Deve retornar:**
```json
{
  "status": "healthy",
  "service": "GLTREND Intelligence Platform",
  "version": "3.0",
  "features": [
    "Early Trend Detection",
    "Momentum Scoring",
    "Opportunity Analysis",
    "Market Overview",
    "Country Insights"
  ]
}
```

### **2. Inteligência Completa**

```bash
https://SUA-URL.up.railway.app/api/intelligence
```

**Aguarde 30-60 segundos** na primeira chamada!

O backend está:
- Buscando Google Trends
- Traduzindo tudo
- Calculando scores
- Analisando mercados

### **3. Produtos Esquentando**

```bash
https://SUA-URL.up.railway.app/api/heating-up
```

**Retorna:** Top 20 produtos com maior oportunidade!

### **4. Market Overview**

```bash
https://SUA-URL.up.railway.app/api/market-overview
```

**Retorna:** Análise de cada mercado (ES, IT, FR, DE, PT)

### **5. País Específico**

```bash
https://SUA-URL.up.railway.app/api/country/ES
https://SUA-URL.up.railway.app/api/country/IT
```

---

## 🐛 TROUBLESHOOTING

### **"Healthcheck failed"**

**Causa:** Timeout ou porta errada

**Solução:**
1. Settings → Start Command
2. DELETE tudo (deixe vazio)
3. O railway.toml tem o comando correto
4. Redeploy

### **"Module not found: deep_translator"**

**Causa:** requirements.txt não está sendo lido

**Solução:**
1. Verifique se `requirements.txt` está na raiz
2. Deve conter:
   ```
   flask==3.0.0
   flask-cors==4.0.0
   pytrends==4.9.2
   pandas==2.1.4
   requests==2.31.0
   gunicorn==21.2.0
   deep-translator==1.11.4
   ```
3. Redeploy

### **"Takes too long to respond"**

**Causa:** Normal na primeira request!

**Explicação:**
- Está buscando Google Trends
- Traduzindo 60+ produtos
- Calculando todos os scores
- Aguarde 30-60s

**Depois fica rápido** (cache de 1 hora)

### **"Empty data"**

**Causa:** Google Trends bloqueou temporariamente

**Solução:**
1. Aguarde 30 minutos
2. Tente endpoint: `POST /api/refresh`
3. Se persistir: use VPN no servidor

---

## 📊 ENDPOINTS DISPONÍVEIS

### **GET /api/intelligence**
Tudo de uma vez (demora ~60s primeira vez)

### **GET /api/heating-up** ⭐
Produtos esquentando (rápido, usa cache)

### **GET /api/market-overview**
Visão dos mercados (rápido)

### **GET /api/country/ES**
Espanha específico (ou IT, FR, DE, PT)

### **POST /api/refresh**
Force refresh (ignora cache, demora ~60s)

### **GET /api/health**
Health check (instantâneo)

---

## ⏱️ PERFORMANCE

### **Primeira chamada:**
- `/api/intelligence`: 30-60s (busca tudo)
- `/api/health`: <1s

### **Com cache (1 hora):**
- Todas as rotas: <1s
- Super rápido!

### **Cache expira:**
- Após 1 hora
- Próxima chamada busca dados frescos
- Depois rápido de novo

---

## 💡 DICAS

### **1. Usar cache**

O cache de 1 hora é PROPOSITAL:
- ✅ Evita bloqueio do Google
- ✅ Performance máxima
- ✅ Economiza requests

### **2. Refresh manual**

Só force refresh quando REALMENTE precisar:

```bash
curl -X POST https://SUA-URL.up.railway.app/api/refresh
```

### **3. Monitorar logs**

No Railway:
- Clique no deployment
- Aba **Logs**
- Veja o que está acontecendo em tempo real

Você verá:
```
📊 Fetching trends for ES...
  ✓ #1 Portable Blender - Opp:9.4 Mom:8.7 Sat:3.4
  ✓ #2 LED Face Mask - Opp:8.9 Mom:8.2 Sat:4.1
...
🔥 Found 15 products heating up!
```

### **4. Custom Domain**

1. Settings → Networking
2. Add Custom Domain
3. Digite: `api.gltrend.com`
4. Configure DNS (CNAME)
5. Pronto!

---

## 🎯 EXEMPLO DE USO COMPLETO

```bash
# 1. Ver produtos esquentando
curl https://gltrend-backend-xxx.up.railway.app/api/heating-up

# 2. Filtrar por Opportunity > 8
# (fazer no frontend)

# 3. Ver detalhes do país
curl https://gltrend-backend-xxx.up.railway.app/api/country/ES

# 4. Ver market overview
curl https://gltrend-backend-xxx.up.railway.app/api/market-overview

# 5. Force refresh se precisar
curl -X POST https://gltrend-backend-xxx.up.railway.app/api/refresh
```

---

## ✅ CHECKLIST FINAL

```
✅ Código no GitHub
✅ Railway: projeto criado/atualizado
✅ Deploy concluído (verde)
✅ Domain gerado
✅ /api/health retorna OK
✅ /api/intelligence funciona (demora primeira vez)
✅ /api/heating-up retorna produtos
✅ Logs mostram dados sendo processados
```

**Tudo ✅ = FUNCIONANDO!** 🎉

---

## 🚀 PRÓXIMO PASSO

**Conectar no FRONTEND!**

Variável de ambiente no frontend:
```
NEXT_PUBLIC_API_URL=https://gltrend-backend-xxx.up.railway.app
```

**Não precisa** do `/api/trends`!

Os endpoints agora são:
- `/api/intelligence`
- `/api/heating-up`
- `/api/market-overview`
- `/api/country/<code>`

---

## 💰 CUSTOS

### **Free tier Railway:**
- $5 crédito/mês
- ~500 horas

### **Uso estimado GLTREND:**
- $2-4/mês (dentro do grátis!)

### **Se precisar mais:**
- Hobby: $5/mês
- Pro: $20/mês

---

## 🎊 PRONTO!

**Seu backend de INTELIGÊNCIA está no ar!** 🚀

Agora é só conectar o frontend e ter uma **plataforma de inteligência de mercado profissional!**

**Boa sorte!** 💪
