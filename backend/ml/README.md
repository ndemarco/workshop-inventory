# AI/ML Module (Phase 4)

Semantic search and intelligent item matching using transformer models.

## Status: 🚧 Planned

## Features

### 1. Semantic Search
Natural language queries with ranked results:

```python
Query: "long metric bolt, M6 diameter"

Results (ranked by relevance):
1. M6 hex bolt, 50mm, zinc plated (95% match) - Zeus:1:A5
2. M6 socket cap screw, 60mm, stainless (87% match) - Muse:2:C2
3. M6 carriage bolt, 75mm, mild steel (82% match) - Zeus:3:B1
```

### 2. Duplicate Detection
Identify similar items during entry:

```python
User adds: "Pan head phillips #8 screw 3/4 inch"

System finds similar:
- "Phillips pan head screw, #8, 19mm" in Zeus:2:B4 (92% similar)
- "#8 pan head machine screw 0.75 inch" in Muse:1:A3 (88% similar)

Prompt: "Similar items found. Add anyway or check existing?"
```

### 3. Specification Extraction
Parse natural language descriptions:

```python
Input: "M6 hex bolt, 50mm long, zinc plated, grade 8.8"

Extracted:
- item_type: "bolt"
- head_style: "hex"  
- thread: "M6"
- length: "50mm"
- coating: "zinc plated"
- grade: "8.8"
- category: "fasteners"
```

### 4. Smart Location Suggestions
Recommend storage locations based on item characteristics:

```python
Item: "0402 SMT resistor, 1kΩ"

Suggestions:
1. Small_parts:1:A1 (tiny bins, perfect size) ✓
2. Small_parts:1:A2 (adjacent to similar items) ✓
3. Electronics:2:C4 (electronics section) ~
❌ Muse:4:B3 (too large, wrong category)
```

## Technical Implementation

### Model Selection

**Primary: sentence-transformers/all-MiniLM-L6-v2**
- Size: 80MB
- Embedding dim: 384
- Speed: ~3000 sentences/sec on CPU
- Good balance of speed/accuracy

**Alternative: sentence-transformers/all-mpnet-base-v2**
- Size: 420MB
- Embedding dim: 768
- Speed: ~1200 sentences/sec on CPU
- Higher accuracy, slower

### Architecture

```python
# ml/semantic_search.py
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSearch:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache = {}
    
    def embed_item(self, item):
        """Create embedding for item description"""
        text = f"{item.name} {item.description} {item.category}"
        return self.model.encode(text, convert_to_tensor=False)
    
    def search(self, query, items, top_k=5):
        """Search items by semantic similarity"""
        query_embedding = self.model.encode(query)
        
        # Get all item embeddings (cached)
        item_embeddings = [self.get_embedding(item) for item in items]
        
        # Calculate similarities
        similarities = cosine_similarity([query_embedding], item_embeddings)[0]
        
        # Get top k
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = [
            {
                'item': items[i],
                'score': similarities[i],
                'location': items[i].location.full_address() if items[i].location else None
            }
            for i in top_indices
            if similarities[i] > 0.3  # Threshold
        ]
        
        return results
    
    def find_similar(self, item, items, threshold=0.8):
        """Find duplicate/similar items"""
        item_emb = self.embed_item(item)
        
        similar = []
        for other in items:
            if other.id == item.id:
                continue
                
            other_emb = self.get_embedding(other)
            similarity = cosine_similarity([item_emb], [other_emb])[0][0]
            
            if similarity > threshold:
                similar.append({
                    'item': other,
                    'similarity': similarity
                })
        
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)
```

### Specification Extraction

```python
# ml/spec_extractor.py
import spacy
import re

class SpecificationExtractor:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.patterns = {
            'thread': r'M\d+|#\d+|\d+/\d+"',
            'length': r'\d+\.?\d*\s?(mm|cm|m|inch|in|")',
            'diameter': r'\d+\.?\d*\s?(mm|cm|inch)?\s?dia',
            'voltage': r'\d+\.?\d*\s?V',
            'resistance': r'\d+\.?\d*\s?(Ω|ohm|k|M)',
            'capacitance': r'\d+\.?\d*\s?(pF|nF|µF|uF|mF)',
        }
    
    def extract(self, description):
        """Extract specifications from natural language"""
        doc = self.nlp(description.lower())
        
        specs = {}
        
        # Extract using regex patterns
        for spec_name, pattern in self.patterns.items():
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                specs[spec_name] = match.group(0)
        
        # Extract entities (material, brand, etc.)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT']:
                specs['brand'] = ent.text
            elif ent.label_ == 'MATERIAL':
                specs['material'] = ent.text
        
        # Determine category
        specs['category'] = self._classify_category(description, doc)
        
        return specs
    
    def _classify_category(self, text, doc):
        """Classify item category"""
        categories = {
            'fasteners': ['bolt', 'screw', 'nut', 'washer', 'rivet'],
            'electronics': ['resistor', 'capacitor', 'ic', 'transistor', 'led'],
            'tools': ['wrench', 'screwdriver', 'pliers', 'hammer'],
            'consumables': ['wire', 'solder', 'flux', 'tape'],
        }
        
        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(kw in text_lower for kw in keywords):
                return category
        
        return 'other'
```

### Database Schema Addition

```python
# Add to models.py
class Item(db.Model):
    # ... existing fields ...
    
    # AI/ML fields
    embedding = db.Column(db.ARRAY(db.Float), nullable=True)  # Store embedding vector
    embedding_updated_at = db.Column(db.DateTime)
    
    def update_embedding(self, semantic_search):
        """Update item embedding"""
        self.embedding = semantic_search.embed_item(self).tolist()
        self.embedding_updated_at = datetime.utcnow()
```

### Caching Strategy

```python
# ml/cache.py
import redis
import pickle

class EmbeddingCache:
    def __init__(self, redis_url='redis://localhost:6379/0'):
        self.redis = redis.from_url(redis_url)
    
    def get(self, item_id):
        """Get cached embedding"""
        key = f"embedding:{item_id}"
        data = self.redis.get(key)
        return pickle.loads(data) if data else None
    
    def set(self, item_id, embedding, ttl=86400):
        """Cache embedding for 24 hours"""
        key = f"embedding:{item_id}"
        self.redis.setex(key, ttl, pickle.dumps(embedding))
```

## API Endpoints

```python
# New routes in backend/app/routes/search.py

@bp.route('/api/search/semantic', methods=['POST'])
def semantic_search():
    """Semantic search endpoint"""
    query = request.json.get('query')
    top_k = request.json.get('top_k', 10)
    
    searcher = SemanticSearch()
    items = Item.query.all()
    
    results = searcher.search(query, items, top_k)
    
    return jsonify({
        'query': query,
        'results': [
            {
                'item': r['item'].to_dict(),
                'score': float(r['score']),
                'location': r['location']
            }
            for r in results
        ]
    })

@bp.route('/api/items/similar/<int:item_id>', methods=['GET'])
def find_similar_items(item_id):
    """Find similar items"""
    item = Item.query.get_or_404(item_id)
    items = Item.query.filter(Item.id != item_id).all()
    
    searcher = SemanticSearch()
    similar = searcher.find_similar(item, items, threshold=0.75)
    
    return jsonify({
        'item_id': item_id,
        'similar_items': [
            {
                'item': s['item'].to_dict(),
                'similarity': float(s['similarity'])
            }
            for s in similar
        ]
    })
```

## Performance Considerations

### Model Loading
- Load model once at startup
- Keep in memory (80-420MB depending on model)
- Use model server for multiple processes

### Embedding Generation
- Generate on item creation/update
- Cache in database
- Batch process for bulk imports

### Search Performance
- Pre-compute all embeddings
- Use FAISS for large inventories (>10k items)
- Implement pagination

### Edge Deployment (Jetson Nano)
- Use quantized models (ONNX)
- Batch inference
- GPU acceleration available

## Dependencies

```python
# Add to requirements.txt
sentence-transformers==2.2.2
torch==2.1.0
transformers==4.35.0
scikit-learn==1.3.2
spacy==3.7.2
redis==5.0.1
faiss-cpu==1.7.4  # or faiss-gpu for GPU support
```

## Testing

```bash
# Test semantic search
python ml/test_semantic.py

# Benchmark performance
python ml/benchmark.py

# Evaluate accuracy
python ml/evaluate.py
```

---

*This feature is planned for Phase 4 development.*
