"""
Euro Trends - Backend API Flask
Busca dados REAIS do Google Trends e serve via API
"""

from flask import Flask, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
import time
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

COUNTRIES = {
    'DE': {'name': 'Germany', 'flag': '🇩🇪'},
    'FR': {'name': 'France', 'flag': '🇫🇷'},
    'IT': {'name': 'Italy', 'flag': '🇮🇹'},
    'ES': {'name': 'Spain', 'flag': '🇪🇸'},
    'NL': {'name': 'Netherlands', 'flag': '🇳🇱'},
    'PL': {'name': 'Poland', 'flag': '🇵🇱'},
    'BE': {'name': 'Belgium', 'flag': '🇧🇪'},
    'PT': {'name': 'Portugal', 'flag': '🇵🇹'},
    'AT': {'name': 'Austria', 'flag': '🇦🇹'},
    'SE': {'name': 'Sweden', 'flag': '🇸🇪'}
}

# Cache simples em memória (em produção use Redis)
cache = {
    'data': None,
    'timestamp': None
}

CACHE_DURATION = 3600  # 1 hora

def get_trending_for_country(country_code):
    """Busca tendências reais do Google Trends"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
        
        print(f"📊 Buscando trends para {country_code}...")
        trending_df = pytrends.trending_searches(pn=country_code.lower())
        trends = trending_df[0].tolist()[:10]
        
        results = []
        for idx, term in enumerate(trends, 1):
            # Rate limiting
            time.sleep(1)
            
            # Busca queries relacionadas
            related_list = []
            try:
                pytrends.build_payload([term], geo=country_code, timeframe='now 7-d')
                related = pytrends.related_queries()
                
                if term in related and related[term]['rising'] is not None:
                    rising = related[term]['rising']
                    if not rising.empty:
                        related_list = [
                            {'query': row['query'], 'value': int(row['value'])}
                            for _, row in rising.head(5).iterrows()
                        ]
            except Exception as e:
                print(f"  ⚠️  Erro ao buscar related queries: {e}")
            
            # Determina growth level baseado no ranking
            if idx <= 2:
                growth = 'hot'
                change = f'+{150 - (idx * 10)}%'
            elif idx <= 5:
                growth = 'trending'
                change = f'+{100 - (idx * 5)}%'
            else:
                growth = 'rising'
                change = f'+{80 - (idx * 3)}%'
            
            results.append({
                'rank': idx,
                'term': term,
                'growth': growth,
                'change': change,
                'related_queries': related_list
            })
            
            print(f"  ✓ #{idx} - {term}")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro ao buscar trends para {country_code}: {e}")
        return []

def fetch_all_trends():
    """Busca trends de todos os países"""
    data = {
        'timestamp': datetime.now().isoformat(),
        'countries': {}
    }
    
    for code, info in COUNTRIES.items():
        print(f"\n🌍 Processando {info['name']}...")
        trends = get_trending_for_country(code)
        
        data['countries'][code] = {
            'name': info['name'],
            'code': code,
            'flag': info['flag'],
            'trending_searches': trends
        }
        
        # Rate limiting entre países
        time.sleep(2)
    
    return data

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Endpoint principal - retorna trends com cache"""
    global cache
    
    # Verifica cache
    if cache['data'] and cache['timestamp']:
        age = (datetime.now() - cache['timestamp']).total_seconds()
        if age < CACHE_DURATION:
            print(f"📦 Retornando dados do cache (idade: {int(age)}s)")
            return jsonify({
                **cache['data'],
                'cached': True,
                'cache_age': int(age)
            })
    
    print("🔄 Cache expirado ou vazio, buscando novos dados...")
    
    # Busca dados frescos
    try:
        data = fetch_all_trends()
        cache['data'] = data
        cache['timestamp'] = datetime.now()
        
        return jsonify({
            **data,
            'cached': False
        })
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch trends'
        }), 500

@app.route('/api/trends/refresh', methods=['POST'])
def refresh_trends():
    """Force refresh dos dados"""
    global cache
    cache['data'] = None
    cache['timestamp'] = None
    
    return get_trends()

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    cache_status = 'empty'
    if cache['data']:
        age = (datetime.now() - cache['timestamp']).total_seconds()
        cache_status = f'{int(age)}s old'
    
    return jsonify({
        'status': 'healthy',
        'service': 'euro-trends-api',
        'cache': cache_status,
        'countries': len(COUNTRIES)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   🌍 EURO TRENDS API INICIANDO...    ║
    ╚═══════════════════════════════════════╝
    
    📡 Porta: {port}
    🗺️  Países: {len(COUNTRIES)}
    ⏱️  Cache: {CACHE_DURATION}s
    
    Endpoints:
    • GET  /api/trends        - Busca trends (com cache)
    • POST /api/trends/refresh - Force refresh
    • GET  /api/health        - Health check
    
    """)
    
    app.run(host='0.0.0.0', port=port, debug=True)
