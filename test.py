#!/usr/bin/env python3
"""
Teste rápido do backend - verifica se tudo funciona
"""

import sys

def test_imports():
    """Testa se as bibliotecas estão instaladas"""
    print("🧪 Testando imports...")
    
    try:
        import flask
        print("  ✅ Flask")
    except ImportError:
        print("  ❌ Flask não instalado! Execute: pip install flask")
        return False
    
    try:
        import flask_cors
        print("  ✅ Flask-CORS")
    except ImportError:
        print("  ❌ Flask-CORS não instalado! Execute: pip install flask-cors")
        return False
    
    try:
        from pytrends.request import TrendReq
        print("  ✅ pytrends")
    except ImportError:
        print("  ❌ pytrends não instalado! Execute: pip install pytrends")
        return False
    
    return True

def test_google_trends():
    """Testa conexão com Google Trends"""
    print("\n🌍 Testando Google Trends API...")
    
    try:
        from pytrends.request import TrendReq
        import time
        
        pytrends = TrendReq(hl='en-US', tz=360)
        
        print("  Buscando trending searches da Alemanha...")
        trending = pytrends.trending_searches(pn='germany')
        
        if not trending.empty:
            print(f"  ✅ Sucesso! Encontrados {len(trending)} trends")
            print(f"\n  Top 3 trends na Alemanha:")
            for i, term in enumerate(trending[0].head(3), 1):
                print(f"    #{i} - {term}")
            return True
        else:
            print("  ⚠️  Nenhum dado retornado")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        print("\n  💡 Isso pode acontecer por:")
        print("     - Rate limiting do Google")
        print("     - Bloqueio temporário")
        print("     - Problema de conexão")
        print("\n  Tente novamente em alguns minutos ou use VPN")
        return False

def run_local_server():
    """Instrução para rodar servidor"""
    print("\n" + "="*50)
    print("📡 COMO RODAR O SERVIDOR:")
    print("="*50)
    print("\n1. Certifique-se que está na pasta backend-python:")
    print("   cd backend-python")
    print("\n2. Instale dependências:")
    print("   pip install -r requirements.txt")
    print("\n3. Rode o servidor:")
    print("   python app.py")
    print("\n4. Acesse:")
    print("   http://localhost:5000/api/health")
    print("   http://localhost:5000/api/trends")
    print("\n5. No frontend (Vercel), adicione env var:")
    print("   NEXT_PUBLIC_API_URL=http://localhost:5000/api/trends")
    print("\n" + "="*50)

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║   🧪 EURO TRENDS - TEST SUITE        ║
    ╚═══════════════════════════════════════╝
    """)
    
    # Teste 1: Imports
    if not test_imports():
        print("\n❌ Instale as dependências primeiro!")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Teste 2: Google Trends
    if not test_google_trends():
        print("\n⚠️  Google Trends não está acessível no momento")
        print("   Mas você pode tentar rodar o servidor mesmo assim")
    
    # Instruções
    run_local_server()
    
    print("\n✅ Testes concluídos!\n")
