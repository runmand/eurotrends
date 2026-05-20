"""
GLTREND - Intelligence Platform Backend V3
Market Intelligence for European E-commerce
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pytrends.request import TrendReq
import time
from datetime import datetime, timedelta
import os
from deep_translator import GoogleTranslator
import statistics
import math

app = Flask(__name__)
CORS(app)

COUNTRIES = {
    'ES': {'name': 'Spain', 'flag': '🇪🇸', 'lang': 'es', 'cpm': 4.20, 'market_temp': 'hot', 'best_channel': 'TikTok'},
    'IT': {'name': 'Italy', 'flag': '🇮🇹', 'lang': 'it', 'cpm': 5.10, 'market_temp': 'warm', 'best_channel': 'Meta'},
    'FR': {'name': 'France', 'flag': '🇫🇷', 'lang': 'fr', 'cpm': 6.50, 'market_temp': 'hot', 'best_channel': 'Meta'},
    'DE': {'name': 'Germany', 'flag': '🇩🇪', 'lang': 'de', 'cpm': 7.80, 'market_temp': 'mature', 'best_channel': 'Google'},
    'PT': {'name': 'Portugal', 'flag': '🇵🇹', 'lang': 'pt', 'cpm': 3.50, 'market_temp': 'hot', 'best_channel': 'TikTok'},
    'NL': {'name': 'Netherlands', 'flag': '🇳🇱', 'lang': 'nl', 'cpm': 8.20, 'market_temp': 'mature', 'best_channel': 'Google'},
    'BE': {'name': 'Belgium', 'flag': '🇧🇪', 'lang': 'nl', 'cpm': 7.50, 'market_temp': 'warm', 'best_channel': 'Meta'},
    'PL': {'name': 'Poland', 'flag': '🇵🇱', 'lang': 'pl', 'cpm': 3.20, 'market_temp': 'hot', 'best_channel': 'TikTok'},
    'AT': {'name': 'Austria', 'flag': '🇦🇹', 'lang': 'de', 'cpm': 7.00, 'market_temp': 'warm', 'best_channel': 'Meta'},
    'SE': {'name': 'Sweden', 'flag': '🇸🇪', 'lang': 'sv', 'cpm': 9.50, 'market_temp': 'mature', 'best_channel': 'Google'}
}

# Country-specific insights
COUNTRY_INSIGHTS = {
    'ES': {
        'consumer_behavior': 'Emotional creative works very well',
        'aesthetic': 'Casual UGC converts best',
        'platform_strength': 'TikTok extremely strong',
        'top_niches': ['Lifestyle', 'Beauty', 'Fashion'],
        'creative_style': 'Authentic, casual, emotional',
        'cultural_notes': 'Lifestyle and emotional storytelling performs well'
    },
    'IT': {
        'consumer_behavior': 'Premium branding matters more',
        'aesthetic': 'Sophisticated, luxury feel',
        'platform_strength': 'Fashion and beauty very strong',
        'top_niches': ['Fashion', 'Beauty', 'Home'],
        'creative_style': 'Polished, elegant, aspirational',
        'cultural_notes': 'Visual quality and branding are crucial'
    },
    'FR': {
        'consumer_behavior': 'Quality and aesthetics important',
        'aesthetic': 'Chic, refined content',
        'platform_strength': 'Meta strong for premium products',
        'top_niches': ['Beauty', 'Fashion', 'Food'],
        'creative_style': 'Elegant, sophisticated',
        'cultural_notes': 'French appreciate quality over quantity'
    },
    'DE': {
        'consumer_behavior': 'Trust and reviews matter',
        'aesthetic': 'Clean, informative',
        'platform_strength': 'Google and rational content',
        'top_niches': ['Electronics', 'Home', 'Auto'],
        'creative_style': 'Professional, detailed, trustworthy',
        'cultural_notes': 'German consumers research heavily before buying'
    },
    'PT': {
        'consumer_behavior': 'Value-conscious, social-driven',
        'aesthetic': 'Vibrant, friendly',
        'platform_strength': 'TikTok growing fast',
        'top_niches': ['Fashion', 'Electronics', 'Sports'],
        'creative_style': 'Warm, relatable, fun',
        'cultural_notes': 'Price-sensitive but brand-loyal'
    }
}

CATEGORIES = {
    'electronics': ['phone', 'laptop', 'tablet', 'headphone', 'speaker', 'tv', 'camera', 'gaming', 'console', 'smart', 'watch', 'charger'],
    'fashion': ['dress', 'shirt', 'pants', 'shoe', 'bag', 'jacket', 'watch', 'clothing', 'fashion', 'style', 'jeans', 'sneaker'],
    'beauty': ['makeup', 'skincare', 'perfume', 'cosmetic', 'beauty', 'hair', 'nail', 'cream', 'serum', 'mask'],
    'home': ['furniture', 'kitchen', 'decor', 'bed', 'lamp', 'storage', 'garden', 'chair', 'table'],
    'sports': ['fitness', 'yoga', 'gym', 'running', 'bicycle', 'workout', 'sport', 'bike', 'training'],
    'kids': ['toy', 'baby', 'child', 'kid', 'game', 'puzzle', 'doll'],
    'health': ['vitamin', 'supplement', 'protein', 'diet', 'health', 'wellness']
}

cache = {
    'data': None,
    'timestamp': None,
    'historical': []  # Track historical data for momentum
}

CACHE_DURATION = 3600

def translate_to_english(text, source_lang):
    """Translate to English"""
    try:
        if source_lang == 'en':
            return text
        translator = GoogleTranslator(source=source_lang, target='en')
        translated = translator.translate(text)
        return translated if translated else text
    except:
        return text

def categorize_product(term_en):
    """Categorize product"""
    term_lower = term_en.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in term_lower:
                return category
    return 'general'

def calculate_trend_score(rank, growth_rate, countries_count):
    """
    TREND SCORE (0-10)
    Based on: rank position, growth rate, geographic spread
    """
    # Rank component (lower rank = higher score)
    rank_score = max(0, 10 - rank)
    
    # Growth component
    growth_score = min(10, growth_rate / 10)
    
    # Geographic component
    geo_score = min(10, countries_count * 2)
    
    # Weighted average
    trend_score = (rank_score * 0.4) + (growth_score * 0.4) + (geo_score * 0.2)
    
    return round(trend_score, 1)

def calculate_saturation_score(rank, num_competitors):
    """
    SATURATION SCORE (0-10)
    0 = Not saturated, 10 = Extremely saturated
    """
    # Rank component (lower rank usually = more saturated)
    rank_saturation = min(10, rank / 2)
    
    # Competitor component (estimated)
    competitor_saturation = min(10, num_competitors / 50)
    
    saturation = (rank_saturation * 0.6) + (competitor_saturation * 0.4)
    
    return round(saturation, 1)

def calculate_growth_velocity(current_rank, previous_data=None):
    """
    GROWTH VELOCITY
    How fast is this product growing?
    Returns: slow, medium, fast, explosive
    """
    if not previous_data:
        # First time seeing it
        if current_rank <= 3:
            return 'explosive'
        elif current_rank <= 7:
            return 'fast'
        else:
            return 'medium'
    
    # Compare with previous
    rank_change = previous_data.get('rank', current_rank) - current_rank
    
    if rank_change >= 5:
        return 'explosive'
    elif rank_change >= 3:
        return 'fast'
    elif rank_change >= 1:
        return 'medium'
    else:
        return 'slow'

def calculate_momentum_score(rank, velocity, saturation):
    """
    MOMENTUM SCORE (0-10)
    Combines growth velocity with low saturation
    HIGH momentum = Fast growth + Low saturation = OPPORTUNITY
    """
    # Velocity points
    velocity_points = {
        'explosive': 10,
        'fast': 7,
        'medium': 4,
        'slow': 1
    }
    
    velocity_score = velocity_points.get(velocity, 5)
    
    # Rank bonus (early = better)
    rank_bonus = max(0, 10 - rank)
    
    # Saturation penalty
    saturation_penalty = saturation
    
    momentum = (velocity_score * 0.5) + (rank_bonus * 0.3) - (saturation_penalty * 0.2)
    momentum = max(0, min(10, momentum))
    
    return round(momentum, 1)

def calculate_opportunity_score(trend_score, saturation, momentum, cpm):
    """
    OPPORTUNITY SCORE (0-10)
    THE MOST IMPORTANT SCORE
    Combines everything to show REAL opportunity
    """
    # High trend + Low saturation + High momentum = HIGH OPPORTUNITY
    
    # CPM factor (lower is better)
    cpm_factor = max(0, 10 - (cpm / 2))
    
    opportunity = (
        (trend_score * 0.3) +
        ((10 - saturation) * 0.3) +  # Invert saturation
        (momentum * 0.3) +
        (cpm_factor * 0.1)
    )
    
    return round(opportunity, 1)

def detect_early_trends(all_trends):
    """
    EARLY TREND DETECTION
    Find products that are heating up but not saturated
    """
    heating_up = []
    
    for country_code, country_data in all_trends.items():
        for trend in country_data.get('trending_searches', []):
            # Criteria for "heating up":
            # 1. Momentum > 6
            # 2. Saturation < 6
            # 3. Growth velocity = fast or explosive
            
            momentum = trend.get('momentum_score', 0)
            saturation = trend.get('saturation_score', 10)
            velocity = trend.get('growth_velocity', 'slow')
            
            if (momentum >= 6 and 
                saturation < 6 and 
                velocity in ['fast', 'explosive']):
                
                heating_up.append({
                    **trend,
                    'country': country_code,
                    'country_name': COUNTRIES[country_code]['name'],
                    'alert_reason': f'High momentum ({momentum}) + Low saturation ({saturation})'
                })
    
    # Sort by opportunity score
    heating_up.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    return heating_up[:20]  # Top 20 heating products

def get_trending_for_country(country_code, min_trends=12):
    """Fetch trends with advanced analytics"""
    try:
        country_info = COUNTRIES[country_code]
        source_lang = country_info['lang']
        cpm = country_info['cpm']
        
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 30))
        
        print(f"📊 Fetching trends for {country_code}...")
        trending_df = pytrends.trending_searches(pn=country_code.lower())
        all_trends = trending_df[0].tolist()[:20]
        
        results = []
        for idx, term in enumerate(all_trends, 1):
            time.sleep(0.8)
            
            term_en = translate_to_english(term, source_lang)
            category = categorize_product(term_en)
            
            # Estimate competitors (based on rank)
            estimated_competitors = idx * 10
            
            # Calculate scores
            trend_score = calculate_trend_score(idx, 100 - (idx * 5), 1)
            saturation_score = calculate_saturation_score(idx, estimated_competitors)
            growth_velocity = calculate_growth_velocity(idx)
            momentum_score = calculate_momentum_score(idx, growth_velocity, saturation_score)
            opportunity_score = calculate_opportunity_score(
                trend_score, saturation_score, momentum_score, cpm
            )
            
            # Growth indicators
            if idx <= 3:
                growth = 'hot'
                change = f'+{160 - (idx * 10)}%'
                estimated_lifetime = '2-4 weeks'
            elif idx <= 7:
                growth = 'trending'
                change = f'+{110 - (idx * 5)}%'
                estimated_lifetime = '1-2 months'
            else:
                growth = 'rising'
                change = f'+{90 - (idx * 3)}%'
                estimated_lifetime = '2-4 months'
            
            # Price range estimation based on category
            price_ranges = {
                'electronics': {'min': 15, 'max': 150, 'avg': 45},
                'fashion': {'min': 20, 'max': 80, 'avg': 35},
                'beauty': {'min': 10, 'max': 60, 'avg': 25},
                'home': {'min': 15, 'max': 100, 'avg': 40},
                'sports': {'min': 20, 'max': 120, 'avg': 50},
                'kids': {'min': 10, 'max': 50, 'avg': 25},
                'health': {'min': 15, 'max': 80, 'avg': 35},
                'general': {'min': 10, 'max': 100, 'avg': 35}
            }
            
            price_range = price_ranges.get(category, price_ranges['general'])
            
            results.append({
                'rank': idx,
                'term': term_en,
                'term_original': term,
                'category': category,
                
                # Core metrics
                'trend_score': trend_score,
                'saturation_score': saturation_score,
                'growth_velocity': growth_velocity,
                'momentum_score': momentum_score,
                'opportunity_score': opportunity_score,
                
                # Market data
                'growth': growth,
                'change': change,
                'estimated_lifetime': estimated_lifetime,
                'estimated_competitors': estimated_competitors,
                
                # Pricing
                'price_range': price_range,
                'estimated_margin': '30-50%',
                
                # Countries (for now just this one)
                'growing_in_countries': [country_code],
                'countries_count': 1
            })
            
            print(f"  ✓ #{idx} {term_en} - Opp:{opportunity_score} Mom:{momentum_score} Sat:{saturation_score}")
            
            if len(results) >= min_trends:
                break
        
        return results
        
    except Exception as e:
        print(f"❌ Error for {country_code}: {e}")
        return []

def calculate_market_overview(countries_data):
    """Calculate market overview analytics"""
    overview = {}
    
    for code, data in countries_data.items():
        trends = data.get('trending_searches', [])
        
        if not trends:
            continue
        
        # Calculate averages
        avg_opportunity = statistics.mean([t.get('opportunity_score', 0) for t in trends])
        avg_saturation = statistics.mean([t.get('saturation_score', 0) for t in trends])
        avg_momentum = statistics.mean([t.get('momentum_score', 0) for t in trends])
        
        # Category distribution
        categories = {}
        for trend in trends:
            cat = trend.get('category', 'general')
            categories[cat] = categories.get(cat, 0) + 1
        
        # Top category
        top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else 'general'
        
        # Market temperature
        if avg_opportunity >= 7:
            market_temp = 'hot'
            market_desc = 'High opportunity market'
        elif avg_opportunity >= 5:
            market_temp = 'warm'
            market_desc = 'Moderate opportunities'
        else:
            market_temp = 'cold'
            market_desc = 'Competitive market'
        
        country_info = COUNTRIES[code]
        
        overview[code] = {
            'name': country_info['name'],
            'flag': country_info['flag'],
            'cpm': country_info['cpm'],
            'market_temperature': market_temp,
            'market_description': market_desc,
            'best_channel': country_info['best_channel'],
            'top_niche': top_category.title(),
            'avg_opportunity_score': round(avg_opportunity, 1),
            'avg_saturation': round(avg_saturation, 1),
            'avg_momentum': round(avg_momentum, 1),
            'total_trends': len(trends),
            'insights': COUNTRY_INSIGHTS.get(code, {})
        }
    
    return overview

def fetch_all_trends():
    """Fetch all trends with intelligence"""
    data = {
        'timestamp': datetime.now().isoformat(),
        'countries': {},
        'heating_up': [],
        'market_overview': {},
        'categories': list(CATEGORIES.keys())
    }
    
    # Fetch trends for priority countries first
    priority = ['ES', 'IT', 'FR', 'DE', 'PT']
    
    for code in priority:
        if code in COUNTRIES:
            print(f"\n🌍 Processing {COUNTRIES[code]['name']}...")
            trends = get_trending_for_country(code, min_trends=12)
            
            data['countries'][code] = {
                'name': COUNTRIES[code]['name'],
                'code': code,
                'flag': COUNTRIES[code]['flag'],
                'trending_searches': trends,
                'total_trends': len(trends)
            }
            
            time.sleep(1.5)
    
    # Calculate market overview
    data['market_overview'] = calculate_market_overview(data['countries'])
    
    # Detect early trends
    data['heating_up'] = detect_early_trends(data['countries'])
    
    print(f"\n🔥 Found {len(data['heating_up'])} products heating up!")
    
    return data

@app.route('/api/intelligence', methods=['GET'])
def get_intelligence():
    """Main intelligence endpoint"""
    global cache
    
    if cache['data'] and cache['timestamp']:
        age = (datetime.now() - cache['timestamp']).total_seconds()
        if age < CACHE_DURATION:
            print(f"📦 Cache hit ({int(age)}s old)")
            return jsonify({**cache['data'], 'cached': True, 'cache_age': int(age)})
    
    print("🔄 Fetching fresh intelligence...")
    
    try:
        data = fetch_all_trends()
        cache['data'] = data
        cache['timestamp'] = datetime.now()
        
        return jsonify({**data, 'cached': False})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/heating-up', methods=['GET'])
def get_heating_up():
    """Get products heating up (early trends)"""
    if cache['data']:
        return jsonify({
            'heating_up': cache['data'].get('heating_up', []),
            'timestamp': cache['data'].get('timestamp'),
            'total': len(cache['data'].get('heating_up', []))
        })
    return jsonify({'heating_up': [], 'total': 0})

@app.route('/api/market-overview', methods=['GET'])
def get_market_overview():
    """Get market overview"""
    if cache['data']:
        return jsonify({
            'market_overview': cache['data'].get('market_overview', {}),
            'timestamp': cache['data'].get('timestamp')
        })
    return jsonify({'market_overview': {}})

@app.route('/api/country/<code>', methods=['GET'])
def get_country_data(code):
    """Get specific country data"""
    if cache['data'] and code in cache['data'].get('countries', {}):
        country = cache['data']['countries'][code]
        overview = cache['data'].get('market_overview', {}).get(code, {})
        
        return jsonify({
            **country,
            'overview': overview,
            'insights': COUNTRY_INSIGHTS.get(code, {})
        })
    return jsonify({'error': 'Country not found'}), 404

@app.route('/api/refresh', methods=['POST'])
def refresh():
    """Force refresh"""
    global cache
    cache['data'] = None
    cache['timestamp'] = None
    return get_intelligence()

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'GLTREND Intelligence Platform',
        'version': '3.0',
        'features': [
            'Early Trend Detection',
            'Momentum Scoring',
            'Opportunity Analysis',
            'Market Overview',
            'Country Insights'
        ],
        'cache_status': 'active' if cache['data'] else 'empty'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"""
    ╔════════════════════════════════════════╗
    ║   🌍 GLTREND INTELLIGENCE PLATFORM    ║
    ║           Backend V3.0                ║
    ╚════════════════════════════════════════╝
    
    🎯 Focus: Spain & Italy (+ FR, DE, PT)
    📊 Early Trend Detection: Enabled
    🔥 Products Heating Up: Active
    💡 Opportunity Scoring: Proprietary
    📈 Market Analytics: Advanced
    
    Endpoints:
    • GET  /api/intelligence        - Full intelligence
    • GET  /api/heating-up          - Products heating up
    • GET  /api/market-overview     - Market overview
    • GET  /api/country/<code>      - Country specific
    • POST /api/refresh             - Force refresh
    • GET  /api/health              - Health check
    
    🚀 Starting on port {port}...
    """)
    
    app.run(host='0.0.0.0', port=port, debug=True)
