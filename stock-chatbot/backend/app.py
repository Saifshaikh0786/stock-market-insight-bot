from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import re
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'

# Mapping common company names to stock symbols
COMPANY_TO_SYMBOL = {
    'apple': 'AAPL',
    'tesla': 'TSLA',
    'microsoft': 'MSFT',
    'google': 'GOOG',
    'alphabet': 'GOOGL',
    'amazon': 'AMZN',
    'meta': 'META',
    'facebook': 'META',
    'nvidia': 'NVDA'
}

def extract_stock_symbol(query):
    # Check for uppercase stock symbol first
    match = re.search(r'\b([A-Z]{1,5})\b', query)
    if match:
        return match.group(1).upper()
    
    # If not, check for company names
    for name, symbol in COMPANY_TO_SYMBOL.items():
        if name.lower() in query.lower():
            return symbol
    return None

def get_stock_data(symbol):
    try:
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'Global Quote' not in data or not data['Global Quote']:
            return None
            
        quote = data['Global Quote']
        return {
            'symbol': symbol,
            'price': float(quote['05. price']),
            'change': float(quote['09. change']),
            'pct_change': float(quote['10. change percent'].strip('%'))
        }
    except Exception as e:
        print(f"API Error (price): {e}")
        return None

def get_company_overview(symbol):
    try:
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'Name' not in data:
            return None
        
        return {
            'Name': data.get('Name'),
            'Description': data.get('Description'),
            'Sector': data.get('Sector'),
            'Industry': data.get('Industry'),
            'MarketCap': data.get('MarketCapitalization'),
            'PERatio': data.get('PERatio')
        }
    except Exception as e:
        print(f"API Error (overview): {e}")
        return None

@app.route('/get_insight', methods=['POST'])
def get_insight():
    user_message = request.json.get('message') or request.json.get('topic')
    if not user_message:
        return jsonify({'response': "❌ Please provide a stock-related query"})

    symbol = extract_stock_symbol(user_message)
    if not symbol:
        return jsonify({'response': "❌ Could not identify stock symbol. Try: 'What's the price of AAPL?'"})

    if "tell me about" in user_message.lower() or "information about" in user_message.lower():
        overview = get_company_overview(symbol)
        if not overview:
            return jsonify({'response': f"❌ Could not fetch company info for {symbol}"})
        response = (
            f"<strong>{overview['Name']}</strong><br>"
            f"Sector: {overview['Sector']} | Industry: {overview['Industry']}<br>"
            f"Market Cap: ${overview['MarketCap']}<br>"
            f"P/E Ratio: {overview['PERatio']}<br><br>"
            f"{overview['Description'][:300]}..."
        )
        return jsonify({'response': response})

    stock_data = get_stock_data(symbol)
    if not stock_data:
        return jsonify({'response': f"❌ Could not fetch data for {symbol}. Try again later or check the symbol."})

    direction = "▲" if stock_data['change'] >= 0 else "▼"
    change_class = "positive" if stock_data['change'] >= 0 else "negative"
    
    response = (
        f"<strong>{stock_data['symbol']}</strong><br>"
        f"Price: ${stock_data['price']:.2f}<br>"
        f"Change: <span class='{change_class}'>{direction} {abs(stock_data['change']):.2f} "
        f"({abs(stock_data['pct_change']):.2f}%)</span>"
    )
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
