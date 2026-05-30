"""
GLTREND V4 - Amazon Best Sellers Intelligence
Optimized for Railway deployment
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import statistics
import re
import os
import threading

app = Flask(__name__)
CORS(app)

AMAZON_DOMAINS = {
    'ES': {'domain': 'amazon.es', 'name': 'Spain', 'flag': '🇪🇸', 'currency': '€', 'cpm': 4.20},
    'IT': {'domain': 'amazon.it', 'name': 'Italy', 'flag': '🇮🇹', 'currency': '€', 'cpm': 5.10},
    'FR': {'domain': 'amazon.fr', 'name': 'France', 'flag': '🇫🇷', 'currency': '€', 'cpm': 6.50},
    'DE': {'domain': 'amazon.de', 'name': 'Germany', 'flag': '🇩🇪', 'currency': '€', 'cpm': 7.80},
    'UK': {'domain': 'amazon.co.uk', 'name': 'United Kingdom', 'flag': '🇬🇧', 'currency': '£', 'cpm': 8.50},
}

CATEGORIES = {
    'electronics': {
        'name': 'Electronics',
        'urls': {
            'ES': 'https://www.amazon.es/gp/bestsellers/electronics',
            'IT': 'https://www.amazon.it/gp/bestsellers/electronics',
            'FR': 'https://www.amazon.fr/gp/bestsellers/electronics',
            'DE': 'https://www.amazon.de/gp/bestsellers/electronics',
            'UK': 'https://www.amazon.co.uk/gp/bestsellers/electronics',
        }
    },
    'home': {
        'name': 'Home & Kitchen',
        'urls': {
            'ES': 'https://www.amazon.es/gp/bestsellers/kitchen',
            'IT': 'https://www.amazon.it/gp/bestsellers/kitchen',
            'FR': 'https://www.amazon.fr/gp/bestsellers/kitchen',
            'DE': 'https://www.amazon.de/gp/bestsellers/kitchen',
            'UK': 'https://www.amazon.co.uk/gp/bestsellers/kitchen',
        }
    },
    'beauty': {
        'name': 'Beauty',
        'urls': {
            'ES': 'https://www.amazon.es/gp/bestsellers/beauty',
            'IT': 'https://www.amazon.it/gp/bestsellers/beauty',
            'FR': 'https://www.amazon.fr/gp/bestsellers/beauty',
            'DE': 'https://www.amazon.de/gp/bestsellers/beauty',
            'UK': 'https://www.amazon.co.uk/gp/bestsellers/beauty',
        }
    },
    'sports': {
        'name': 'Sports & Outdoors',
        'urls': {
            'ES': 'https://www.amazon.es/gp/bestsellers/sports',
            'IT': 'https://www.amazon.it/gp/bestsellers/sports',
            'FR': 'https://www.amazon.fr/gp/bestsellers/sports',
            'DE': 'https://www.amazon.de/gp/bestsellers/sports',
            'UK': 'https://www.amazon.co.uk/gp/bestsellers/sports',
        }
    },
    'toys': {
        'name': 'Toys & Games',
        'urls': {
            'ES': 'https://www.amazon.es/gp/bestsellers/toys',
            'IT': 'https://www.amazon.it/gp/bestsellers/toys',
            'FR': 'https://www.amazon.fr/gp/bestsellers/toys',
            'DE': 'https://www.amazon.de/gp/bestsellers/toys',
            'UK': 'https://www.amazon.co.uk/gp/bestsellers/toys',
        }
    },
    'clothing': {
        'name': 'Clothing & Fashion',
        'urls': {
            'ES': 'https://www.amazon.es/gp/bestsellers/fashion',
            'IT': 'https://www.amazon.it/gp/bestsellers/fashion',
            'FR': 'https://www.amazon.fr/gp/bestsellers/fashion',
            'DE': 'https://www.amazon.de/gp/bestsellers/fashion',
            'UK': 'https://www.amazon.co.uk/gp/bestsellers/fashion',
        }
    },
    'health': {
        'name': 'Health & Personal Care',
        'urls': {
            'ES': 'https://www.amazon.es/gp/bestsellers/hpc',
            'IT': 'https://www.amazon.it/gp/bestsellers/hpc',
            'FR': 'https://www.amazon.fr/gp/bestsellers/hpc',
            'DE': 'https://www.amazon.de/gp/bestsellers/hpc',
            'UK': 'https://www.amazon.co.uk/gp/bestsellers/hpc',
        }
    },
    'pet': {
        'name': 'Pet Supplies',
        'urls': {
            'ES': 'https://www.amazon.es/gp/bestsellers/pet-supplies',
            'IT': 'https://www.amazon.it/gp/bestsellers/pet-supplies',
            'FR': 'https://www.amazon.fr/gp/bestsellers/pet-supplies',
            'DE': 'https://www.amazon.de/gp/bestsellers/pet-supplies',
            'UK': 'https://www.amazon.co.uk/gp/bestsellers/pet-supplies',
        }
    },
}

# ─── Cache e estado ────────────────────────────────────────────────────────────
cache = {'data': None, 'timestamp': None}
CACHE_DURATION = 3600
scraping_lock = threading.Lock()
is_scraping = False  # flag para não iniciar dois scrapings ao mesmo tempo

# ─── Headers rotativos ─────────────────────────────────────────────────────────
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
]
_ua_index = 0

def get_headers():
    global _ua_index
    ua = USER_AGENTS[_ua_index % len(USER_AGENTS)]
    _ua_index += 1
    return {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

def extract_price(price_text):
    if not price_text:
        return None
    price_text = price_text.replace('€', '').replace('£', '').replace(',', '.').strip()
    match = re.search(r'(\d+\.?\d*)', price_text)
    if match:
        try:
            return float(match.group(1))
        except:
            return None
    return None

def calculate_scores(rank, price, rating, reviews, total_products):
    trend_score = max(0, 10 - (rank * 0.5))

    if reviews > 10000:
        saturation_score = 9.0
    elif reviews > 5000:
        saturation_score = 7.0
    elif reviews > 1000:
        saturation_score = 5.0
    elif reviews > 500:
        saturation_score = 3.0
    else:
        saturation_score = 1.0

    momentum_score = (trend_score * 0.6) + ((10 - saturation_score) * 0.4)

    if rank <= 3:
        velocity = 'explosive'
        change = f'+{160 - (rank * 10)}%'
    elif rank <= 7:
        velocity = 'fast'
        change = f'+{110 - (rank * 5)}%'
    elif rank <= 12:
        velocity = 'medium'
        change = f'+{90 - (rank * 3)}%'
    else:
        velocity = 'slow'
        change = f'+{max(10, 70 - (rank * 2))}%'

    if price:
        if price < 20:
            price_score = 8.0
        elif price < 50:
            price_score = 9.0
        elif price < 100:
            price_score = 7.0
        else:
            price_score = 5.0
    else:
        price_score = 5.0

    rating_score = (rating * 2) if rating else 5.0

    opportunity_score = (
        (trend_score * 0.25) +
        ((10 - saturation_score) * 0.35) +
        (momentum_score * 0.20) +
        (price_score * 0.10) +
        (rating_score * 0.10)
    )

    return {
        'trend_score': round(trend_score, 1),
        'saturation_score': round(saturation_score, 1),
        'momentum_score': round(momentum_score, 1),
        'opportunity_score': round(opportunity_score, 1),
        'growth_velocity': velocity,
        'change': change,
        'estimated_margin': '30-50%' if price and price < 50 else '20-40%',
        'estimated_lifetime': '2-4 weeks' if rank <= 3 else '1-2 months' if rank <= 7 else '2-4 months'
    }

def generate_alert_reason(rank, scores, price, reviews):
    if rank <= 3 and scores['saturation_score'] < 4:
        return f"Top {rank} com baixa saturação — janela de oportunidade aberta"
    elif scores['opportunity_score'] >= 8:
        return f"Alto score de oportunidade ({scores['opportunity_score']}) com momentum crescente"
    elif price and price < 25 and reviews < 1000:
        return f"Preço acessível (€{price}) e poucos concorrentes estabelecidos"
    elif scores['growth_velocity'] == 'explosive':
        return "Crescimento explosivo detectado nas últimas semanas"
    elif scores['growth_velocity'] == 'fast':
        return f"Crescimento acelerado — #{rank} no ranking com {scores['change']} de crescimento"
    else:
        return f"Produto em ascensão — #{rank} no ranking com potencial identificado"

def scrape_amazon_bestsellers(country_code, category_key, max_products=12):
    try:
        category = CATEGORIES[category_key]
        url = category['urls'].get(country_code)
        if not url:
            return []

        print(f"  📊 Scraping {country_code} - {category['name']}...")

        session = requests.Session()
        response = session.get(url, headers=get_headers(), timeout=15, allow_redirects=True)

        if response.status_code == 503:
            print(f"  ⚠️  503 - aguardando 5s e tentando novamente...")
            time.sleep(5)
            response = session.get(url, headers=get_headers(), timeout=15)

        if response.status_code != 200:
            print(f"  ❌ Failed: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        products = []

        items = soup.find_all('div', {'class': 'zg-grid-general-faceout'})[:max_products]
        if not items:
            items = soup.find_all('div', {'id': re.compile(r'gridItemRoot')})[:max_products]
        if not items:
            items = soup.find_all('li', {'class': re.compile(r'zg-item-immersion')})[:max_products]

        if not items:
            print(f"  ⚠️  Nenhum produto — Amazon pode ter bloqueado")
            return []

        for idx, item in enumerate(items, 1):
            try:
                title_elem = (
                    item.find('div', {'class': '_cDEzb_p13n-sc-css-line-clamp-3_g3dy1'}) or
                    item.find('div', {'class': 'p13n-sc-truncate'}) or
                    item.find('a', {'class': 'a-link-normal'}) or
                    item.find('span', {'class': re.compile(r'p13n-sc')})
                )
                title = title_elem.get_text(strip=True) if title_elem else f"Product #{idx}"

                price_elem = (
                    item.find('span', {'class': 'p13n-sc-price'}) or
                    item.find('span', {'class': 'a-price-whole'}) or
                    item.find('span', {'class': re.compile(r'a-price')})
                )
                price = extract_price(price_elem.get_text(strip=True) if price_elem else None)

                link_elem = item.find('a', href=True)
                product_url = f"https://www.{AMAZON_DOMAINS[country_code]['domain']}{link_elem['href']}" if link_elem else None

                rating_elem = item.find('span', {'class': 'a-icon-alt'})
                rating = None
                if rating_elem:
                    m = re.search(r'(\d+\.?\d*)', rating_elem.get_text(strip=True))
                    if m:
                        rating = float(m.group(1))

                reviews_elem = item.find('span', {'class': 'a-size-small'})
                reviews_text = reviews_elem.get_text(strip=True) if reviews_elem else '0'
                reviews_match = re.search(r'(\d+)', reviews_text.replace(',', '').replace('.', ''))
                reviews = int(reviews_match.group(1)) if reviews_match else 0

                scores = calculate_scores(idx, price, rating, reviews, len(items))
                alert_reason = generate_alert_reason(idx, scores, price, reviews)

                products.append({
                    'rank': idx,
                    'title': title[:100],
                    'price': price,
                    'currency': AMAZON_DOMAINS[country_code]['currency'],
                    'rating': rating,
                    'reviews': reviews,
                    'url': product_url,
                    'category': category_key,
                    'alert_reason': alert_reason,
                    **scores
                })

            except Exception as e:
                print(f"    ⚠️  Error parsing item {idx}: {e}")
                continue

        print(f"  ✅ Got {len(products)} products")
        return products

    except Exception as e:
        print(f"  ❌ Error scraping {country_code} - {category_key}: {e}")
        return []

def fetch_all_data():
    global is_scraping
    
    with scraping_lock:
        if is_scraping:
            print("⏳ Scraping já em andamento, aguardando...")
            return cache.get('data')
        is_scraping = True

    try:
        data = {
            'timestamp': datetime.now().isoformat(),
            'source': 'Amazon Best Sellers',
            'countries': {},
            'heating_up': [],
            'market_overview': {}
        }

        priority_countries = ['ES', 'IT', 'FR', 'DE', 'UK']

        for country_code in priority_countries:
            print(f"\n🌍 Processing {AMAZON_DOMAINS[country_code]['name']}...")
            all_products = []

            for category_key in CATEGORIES.keys():
                products = scrape_amazon_bestsellers(country_code, category_key, max_products=12)
                all_products.extend(products)
                time.sleep(2)

            data['countries'][country_code] = {
                'name': AMAZON_DOMAINS[country_code]['name'],
                'code': country_code,
                'flag': AMAZON_DOMAINS[country_code]['flag'],
                'products': all_products,
                'trending_searches': all_products,
                'total_products': len(all_products),
                'total_trends': len(all_products)
            }

            time.sleep(3)

        # Heating up
        all_flat = []
        for country_code, country_data in data['countries'].items():
            for product in country_data['products']:
                all_flat.append({**product, 'country': country_code, 'country_name': AMAZON_DOMAINS[country_code]['name']})

        heating = [p for p in all_flat if p['momentum_score'] >= 6 and p['saturation_score'] < 6]
        heating.sort(key=lambda x: x['opportunity_score'], reverse=True)
        data['heating_up'] = heating[:30]

        # Market overview com todos os campos que o frontend usa
        for country_code, country_data in data['countries'].items():
            products = country_data['products']
            if products:
                avg_opp = statistics.mean([p['opportunity_score'] for p in products])
                prices = [p['price'] for p in products if p['price']]
                avg_price = statistics.mean(prices) if prices else 0

                niche_counts = {}
                for p in products:
                    cat = p.get('category', 'general')
                    niche_counts[cat] = niche_counts.get(cat, 0) + 1
                top_niche = max(niche_counts, key=niche_counts.get) if niche_counts else 'N/A'

                data['market_overview'][country_code] = {
                    'name': AMAZON_DOMAINS[country_code]['name'],
                    'flag': AMAZON_DOMAINS[country_code]['flag'],
                    'cpm': AMAZON_DOMAINS[country_code]['cpm'],
                    'avg_opportunity_score': round(avg_opp, 1),
                    'avg_opportunity': round(avg_opp, 1),
                    'avg_price': round(avg_price, 2),
                    'currency': AMAZON_DOMAINS[country_code]['currency'],
                    'total_products': len(products),
                    'total_trends': len(products),
                    'top_niche': top_niche,
                    'best_channel': 'Meta Ads' if AMAZON_DOMAINS[country_code]['cpm'] < 6 else 'Google Ads',
                    'market_temperature': 'hot' if avg_opp >= 6 else 'warm',
                }

        print(f"\n🔥 Found {len(data['heating_up'])} products heating up!")

        # Salva no cache
        cache['data'] = data
        cache['timestamp'] = datetime.now()

        return data

    except Exception as e:
        print(f"❌ fetch_all_data error: {e}")
        raise
    finally:
        is_scraping = False


# ─── Rotas ────────────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check — RESPONDE IMEDIATAMENTE sem scraping.
    Railway usa esta rota para saber se o servidor está vivo.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'GLTREND Amazon Intelligence',
        'version': '4.2',
        'cache_status': 'active' if cache['data'] else 'empty',
        'is_scraping': is_scraping,
    })

@app.route('/api/intelligence', methods=['GET'])
def get_intelligence():
    """Main endpoint — só scrapa quando chamado, nunca no boot."""
    global cache

    # Cache válido → devolve imediatamente
    if cache['data'] and cache['timestamp']:
        age = (datetime.now() - cache['timestamp']).total_seconds()
        if age < CACHE_DURATION:
            print(f"📦 Cache hit ({int(age)}s old)")
            return jsonify({**cache['data'], 'cached': True, 'cache_age': int(age)})

    # Se já está scrapando, retorna cache antigo (se tiver) com aviso
    if is_scraping:
        if cache['data']:
            return jsonify({**cache['data'], 'cached': True, 'cache_age': -1, 'updating': True})
        return jsonify({'error': 'Scraping em andamento, tente novamente em 2-3 minutos', 'updating': True}), 503

    print("🔄 Fetching fresh Amazon data...")

    try:
        data = fetch_all_data()
        return jsonify({**data, 'cached': False})
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'message': 'Erro ao buscar dados da Amazon'}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh():
    """Force refresh — limpa cache e rebusca."""
    global cache
    if is_scraping:
        return jsonify({'message': 'Scraping já em andamento'}), 409
    cache['data'] = None
    cache['timestamp'] = None
    return get_intelligence()

@app.route('/api/heating-up', methods=['GET'])
def get_heating():
    if cache['data']:
        return jsonify({'heating_up': cache['data'].get('heating_up', []), 'total': len(cache['data'].get('heating_up', []))})
    return jsonify({'heating_up': [], 'total': 0})

@app.route('/api/market-overview', methods=['GET'])
def get_overview():
    if cache['data']:
        return jsonify({'market_overview': cache['data'].get('market_overview', {}), 'timestamp': cache['data'].get('timestamp')})
    return jsonify({'market_overview': {}})

@app.route('/', methods=['GET'])
def index():
    return jsonify({'service': 'GLTREND API', 'status': 'online', 'endpoints': ['/api/health', '/api/intelligence', '/api/refresh']})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"""
    ╔════════════════════════════════════════╗
    ║   🛒 GLTREND V4.2 - RAILWAY READY      ║
    ╚════════════════════════════════════════╝
    Port: {port}
    Health: http://0.0.0.0:{port}/api/health
    API:    http://0.0.0.0:{port}/api/intelligence
    """)
    app.run(host='0.0.0.0', port=port, debug=False)
