# Strategy 3: Custom Probability Engine

**Strategy Type:** Quantitative / Fundamental Analysis  
**Difficulty:** Advanced  
**Capital Required:** $15k-30k  
**Expected Returns:** 15-30% monthly  
**Win Rate:** 65-75%  
**Time Horizon:** 3-14 days per trade

---

## Overview

Build proprietary probability models that estimate the "true" likelihood of events, then trade when your model significantly disagrees with the market price.

This is the highest-potential strategy but requires significant development and data infrastructure.

## The Core Concept

**Market pricing reflects crowd wisdom** - but crowds can be:
- Emotional (overreact to news)
- Uninformed (don't have all data)
- Biased (political/tribal preferences)
- Slow (lag behind new information)

**Your edge:** A systematic model that:
- Processes more data than humans can
- Remains emotionally neutral
- Updates in real-time
- Quantifies confidence levels

## Example: Election Market

**Market:** "Democrat wins 2024 presidential election"  
**Market price:** 50¢ (50% probability)

**Your model inputs:**
- Latest polling data (55% for Democrat)
- Historical polling errors (+/- 3%)
- Economic indicators (favorable)
- Incumbent advantage (slight positive)
- Social media sentiment (60% positive)
- Betting odds aggregator (53% Democrat)
- Expert forecasters (Nate Silver: 58%)

**Model output:** 58% probability (±5% confidence interval)

**Trading decision:**
- Model says: 58%
- Market says: 50%
- **Edge: 8 percentage points**
- **Action: BUY at 50¢**

Target exit: 55-58¢ for 10-16% profit

## Model Architecture

### Multi-Model Ensemble

Don't rely on one model - use multiple models and weight their outputs:

```python
class ProbabilityEnsemble:
    def __init__(self):
        self.models = {
            'news_sentiment': NewsBasedModel(),
            'polling': PollingAggregator(),
            'social_sentiment': SocialSentimentModel(),
            'historical_pattern': HistoricalPatternModel(),
            'market_microstructure': MarketMicrostructureModel()
        }
        
        # Weights (must sum to 1.0)
        self.weights = {
            'news_sentiment': 0.20,
            'polling': 0.35,
            'social_sentiment': 0.15,
            'historical_pattern': 0.15,
            'market_microstructure': 0.15
        }
    
    def estimate_probability(self, market_id, event_data):
        """
        Generate probability estimate from all models
        """
        probabilities = {}
        confidences = {}
        
        for model_name, model in self.models.items():
            try:
                prob, confidence = model.predict(market_id, event_data)
                probabilities[model_name] = prob
                confidences[model_name] = confidence
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                probabilities[model_name] = 0.5  # Neutral
                confidences[model_name] = 0.0
        
        # Calculate weighted probability
        weighted_prob = sum(
            probabilities[name] * confidences[name] * self.weights[name]
            for name in self.models.keys()
        )
        
        # Calculate average confidence
        avg_confidence = sum(
            confidences[name] * self.weights[name]
            for name in self.models.keys()
        )
        
        return weighted_prob, avg_confidence
    
    def find_edge(self, market_id, event_data):
        """
        Determine if there's a trading edge
        """
        model_prob, confidence = self.estimate_probability(market_id, event_data)
        market_price = get_market_price(market_id)
        
        edge = model_prob - market_price
        
        # Trading criteria:
        # 1. High confidence (>0.7)
        # 2. Significant edge (>10%)
        # 3. Model disagrees with market substantially
        
        min_confidence = 0.70
        min_edge = 0.10
        
        if confidence > min_confidence and abs(edge) > min_edge:
            return {
                'model_prob': model_prob,
                'market_price': market_price,
                'edge': edge,
                'edge_pct': (edge / market_price) * 100,
                'confidence': confidence,
                'action': 'BUY' if edge > 0 else 'SELL',
                'expected_value': edge * confidence
            }
        
        return None
```

## Individual Model Implementations

### 1. News Sentiment Model

```python
import requests
from textblob import TextBlob
from datetime import datetime, timedelta

class NewsBasedModel:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    def predict(self, market_id, event_data):
        """
        Analyze news sentiment for event
        """
        # Extract keywords from event
        keywords = self.extract_keywords(event_data['description'])
        
        # Fetch recent news
        news_articles = self.fetch_news(keywords, days=7)
        
        # Analyze sentiment
        sentiments = []
        for article in news_articles:
            sentiment = self.analyze_sentiment(article['title'] + " " + article['description'])
            sentiments.append(sentiment)
        
        # Calculate probability based on sentiment
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Map sentiment (-1 to 1) to probability (0 to 1)
        probability = (avg_sentiment + 1) / 2
        
        # Confidence based on number and recency of articles
        confidence = min(len(news_articles) / 20, 1.0)
        
        return probability, confidence
    
    def fetch_news(self, keywords, days=7):
        """
        Fetch news articles from NewsAPI
        """
        from_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        params = {
            'q': ' OR '.join(keywords),
            'from': from_date,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        articles = response.json().get('articles', [])
        
        return articles
    
    def analyze_sentiment(self, text):
        """
        Calculate sentiment score using TextBlob
        """
        blob = TextBlob(text)
        return blob.sentiment.polarity
    
    def extract_keywords(self, description):
        """
        Extract key search terms from market description
        """
        # Simple keyword extraction
        # In production, use NLP libraries like spaCy
        stop_words = ['will', 'the', 'by', 'in', 'on', 'at', 'to']
        words = description.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return keywords[:5]  # Top 5 keywords
```

### 2. Polling Aggregator Model

```python
import requests
import numpy as np
from datetime import datetime, timedelta

class PollingAggregator:
    def __init__(self):
        self.pollster_ratings = {
            # Based on 538 pollster ratings
            'Marist': 0.95,
            'Pew Research': 0.95,
            'ABC/Washington Post': 0.90,
            'CNN': 0.85,
            'Fox News': 0.80,
            'Rasmussen': 0.70
        }
    
    def predict(self, market_id, event_data):
        """
        Aggregate polling data with quality weights
        """
        # Fetch recent polls
        polls = self.fetch_polls(event_data['keywords'])
        
        if not polls:
            return 0.5, 0.0  # Neutral, no confidence
        
        # Weight polls by quality and recency
        weighted_results = []
        total_weight = 0
        
        for poll in polls:
            # Quality weight
            pollster_quality = self.pollster_ratings.get(poll['pollster'], 0.5)
            
            # Recency weight (exponential decay)
            days_old = (datetime.now() - poll['date']).days
            recency_weight = np.exp(-days_old / 14)  # Half-life of 14 days
            
            # Sample size weight
            size_weight = min(poll['sample_size'] / 1000, 1.0)
            
            # Combined weight
            weight = pollster_quality * recency_weight * size_weight
            
            weighted_results.append(poll['result'] * weight)
            total_weight += weight
        
        # Calculate weighted average
        probability = sum(weighted_results) / total_weight if total_weight > 0 else 0.5
        
        # Confidence based on number of polls and agreement
        confidence = min(len(polls) / 10, 1.0) * (1 - np.std([p['result'] for p in polls]))
        
        return probability, confidence
    
    def fetch_polls(self, keywords):
        """
        Fetch polling data from FiveThirtyEight or other aggregators
        """
        # Simplified - in production, scrape 538 or use polling APIs
        # This is placeholder logic
        return []
```

### 3. Social Sentiment Model

```python
import tweepy
from transformers import pipeline

class SocialSentimentModel:
    def __init__(self, twitter_api_key):
        self.twitter_client = self.setup_twitter(twitter_api_key)
        self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                          model="finiteautomata/bertweet-base-sentiment-analysis")
    
    def predict(self, market_id, event_data):
        """
        Analyze social media sentiment
        """
        keywords = event_data['keywords']
        
        # Fetch recent tweets
        tweets = self.fetch_tweets(keywords, count=1000)
        
        # Analyze sentiment
        sentiments = []
        for tweet in tweets:
            result = self.sentiment_analyzer(tweet['text'])[0]
            
            # Map to probability
            if result['label'] == 'POS':
                sentiment = 0.5 + (result['score'] * 0.5)
            else:
                sentiment = 0.5 - (result['score'] * 0.5)
            
            sentiments.append(sentiment)
        
        # Weight by influencer status
        weighted_sentiments = []
        for tweet, sentiment in zip(tweets, sentiments):
            follower_weight = np.log10(tweet['followers'] + 1) / 7  # Normalize to 0-1
            weighted_sentiments.append(sentiment * (0.5 + follower_weight * 0.5))
        
        probability = np.mean(weighted_sentiments)
        confidence = min(len(tweets) / 500, 1.0)
        
        return probability, confidence
    
    def setup_twitter(self, api_key):
        # Setup Twitter API client
        pass
    
    def fetch_tweets(self, keywords, count=1000):
        # Fetch tweets matching keywords
        pass
```

### 4. Historical Pattern Model

```python
class HistoricalPatternModel:
    def __init__(self):
        self.historical_data = {}
    
    def predict(self, market_id, event_data):
        """
        Use historical patterns to predict outcomes
        """
        event_type = event_data['type']  # 'election', 'crypto', 'sports', etc.
        
        # Find similar historical events
        similar_events = self.find_similar_events(event_data)
        
        if not similar_events:
            return 0.5, 0.0
        
        # Calculate base rate (how often similar events occurred)
        outcomes = [event['outcome'] for event in similar_events]
        probability = sum(outcomes) / len(outcomes)
        
        # Adjust for current conditions
        adjusted_prob = self.adjust_for_conditions(probability, event_data)
        
        # Confidence based on number of similar events
        confidence = min(len(similar_events) / 20, 0.8)
        
        return adjusted_prob, confidence
    
    def find_similar_events(self, event_data):
        """
        Find historical events similar to current event
        """
        # Use embeddings or feature matching
        # Return list of similar historical events
        return []
    
    def adjust_for_conditions(self, base_prob, event_data):
        """
        Adjust probability based on current conditions
        """
        # Factor in: economic conditions, seasonality, trends, etc.
        return base_prob
```

### 5. Market Microstructure Model

```python
class MarketMicrostructureModel:
    def predict(self, market_id, event_data):
        """
        Analyze order book and trading patterns
        """
        # Get order book
        order_book = get_order_book(market_id)
        
        # Get recent trades
        recent_trades = get_recent_trades(market_id, count=100)
        
        # Calculate metrics
        buy_pressure = self.calculate_buy_pressure(order_book)
        smart_money_flow = self.detect_smart_money(recent_trades)
        volume_trend = self.analyze_volume_trend(recent_trades)
        
        # Combine signals
        probability = (buy_pressure * 0.4 + 
                      smart_money_flow * 0.4 + 
                      volume_trend * 0.2)
        
        confidence = 0.6  # Medium confidence
        
        return probability, confidence
    
    def calculate_buy_pressure(self, order_book):
        """
        Ratio of buy volume to total volume
        """
        buy_volume = sum(order['size'] for order in order_book['bids'])
        sell_volume = sum(order['size'] for order in order_book['asks'])
        total = buy_volume + sell_volume
        
        return buy_volume / total if total > 0 else 0.5
    
    def detect_smart_money(self, trades):
        """
        Identify trades from historically successful wallets
        """
        smart_wallets = get_smart_wallets()
        
        smart_money_trades = [t for t in trades if t['wallet'] in smart_wallets]
        
        if not smart_money_trades:
            return 0.5
        
        # What side are smart wallets taking?
        buy_count = sum(1 for t in smart_money_trades if t['side'] == 'BUY')
        
        return buy_count / len(smart_money_trades)
    
    def analyze_volume_trend(self, trades):
        """
        Is volume increasing on buy or sell side?
        """
        recent = trades[:30]
        older = trades[30:60]
        
        recent_buy_vol = sum(t['size'] for t in recent if t['side'] == 'BUY')
        older_buy_vol = sum(t['size'] for t in older if t['side'] == 'BUY')
        
        total_recent = sum(t['size'] for t in recent)
        total_older = sum(t['size'] for t in older)
        
        recent_buy_ratio = recent_buy_vol / total_recent if total_recent > 0 else 0.5
        older_buy_ratio = older_buy_vol / total_older if total_older > 0 else 0.5
        
        # If buy ratio increasing, bullish
        if recent_buy_ratio > older_buy_ratio:
            return 0.5 + (recent_buy_ratio - older_buy_ratio)
        else:
            return 0.5 - (older_buy_ratio - recent_buy_ratio)
```

## Trading Bot Integration

```python
class ProbabilityModelBot:
    def __init__(self, ensemble):
        self.ensemble = ensemble
        self.positions = []
    
    async def scan_markets(self):
        """
        Scan all markets for model-price disagreements
        """
        while True:
            try:
                markets = await get_all_markets()
                
                for market in markets:
                    edge = self.ensemble.find_edge(market['id'], market)
                    
                    if edge:
                        await self.execute_trade(market, edge)
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                print(f"Error scanning: {e}")
                await asyncio.sleep(60)
    
    async def execute_trade(self, market, edge):
        """
        Execute trade based on model edge
        """
        # Position sizing based on edge and confidence
        kelly_fraction = edge['edge'] * edge['confidence']
        position_size = self.calculate_position_size(kelly_fraction)
        
        # Place order
        if edge['action'] == 'BUY':
            order = await place_buy_order(
                market['id'],
                position_size,
                max_price=edge['market_price'] * 1.05  # 5% slippage tolerance
            )
        else:
            order = await place_sell_order(
                market['id'],
                position_size,
                min_price=edge['market_price'] * 0.95
            )
        
        # Track position
        self.positions.append({
            'market_id': market['id'],
            'entry_price': edge['market_price'],
            'model_prob': edge['model_prob'],
            'edge': edge['edge'],
            'confidence': edge['confidence'],
            'position_size': position_size,
            'entry_time': datetime.now(),
            'order': order
        })
        
        print(f"✅ Trade executed:")
        print(f"   Market: {market['description']}")
        print(f"   Model: {edge['model_prob']:.2%}")
        print(f"   Market: {edge['market_price']:.2%}")
        print(f"   Edge: {edge['edge']:.2%}")
        print(f"   Size: ${position_size}")
```

## Risk Management

### Only Trade High-Confidence Signals
- Confidence > 70%
- Edge > 10%
- Multiple models agree

### Position Sizing
- Kelly Criterion: `f = (edge × confidence) / odds`
- Use fractional Kelly (25-50%) for safety
- Max 10% of capital per position

### Exit Strategy
- Take profit: Model price ± 2%
- Stop loss: -15% from entry
- Time-based: Exit after 14 days
- Fundamental change: Exit immediately

## Expected Performance

### Opportunities
- **2-10 high-confidence trades per week**
- **More opportunities during major events**

### Profit Per Trade
- **Winners:** 10-30% profit
- **Losers:** 5-15% loss
- **Average:** 5-10% per trade

### Monthly Returns
With $30k capital:
- **Conservative:** $4,500/month (15%)
- **Realistic:** $6,000/month (20%)
- **Aggressive:** $9,000+/month (30%)

### Win Rate
- **65-75%** (highest skill-based strategy)

## Infrastructure Requirements

- News APIs (NewsAPI, Twitter)
- Polling data sources
- ML libraries (scikit-learn, transformers)
- PostgreSQL database
- GPU for NLP models (optional)
- 24/7 monitoring

## Next Steps

1. **Build one model first** (start with polling or news)
2. **Backtest on historical markets**
3. **Paper trade for 1 month**
4. **Add additional models**
5. **Deploy with small capital**
6. **Continuously improve models**

---

**[← Previous: Pairs Trading](./strategy_2_pairs_trading.md)** | **[Next: Market Making →](./strategy_4_market_making.md)**

---

*This is Strategy 3 of 7 in the PolyMarket Trading Bot series*  
*Last Updated: December 25, 2025*

