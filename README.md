# 🔍 AI-Powered Petition Search System

A natural language search interface for UK Parliament petitions using semantic search and AI embeddings.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Overview

This project enables users to search UK Parliament petitions using natural language queries like "Find me all petitions about education" or "Show me campaigns calling for environmental protection". Unlike traditional keyword search, this system understands the **meaning** behind queries using AI-powered semantic search.

<p align="center">
  <img width="1370" alt="image" src="https://github.com/user-attachments/assets/89126202-fc81-4e9d-b02a-df85f4151e96" />
</p>

<p align="center">
  <img width="1370" alt="image" src="https://github.com/user-attachments/assets/f4172c20-ead5-4eea-8b57-98353ae230be" />
</p>



### Key Features
- 🤖 **Semantic Search**: Uses Sentence Transformers to understand query meaning
- 🎯 **High Relevance**: Returns results based on semantic similarity, not just keywords
- 🚀 **Fast Performance**: Embeddings are cached for quick responses
- 📊 **Search Analytics**: Visual charts showing query coverage and petition statistics
- 🔧 **RESTful API**: Clean API design with automatic documentation
- 💻 **Responsive UI**: Works on desktop and mobile devices with interactive charts
- 🔒 **Security Aware**: Input validation, CORS handling, XSS prevention

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  HTML/CSS/JS - Clean, responsive interface
│   (Browser)     │  
└────────┬────────┘
         │ HTTP/JSON
         ▼
┌─────────────────┐
│   FastAPI       │  REST API with automatic documentation
│   Backend       │  
├─────────────────┤
│  Search Engine  │  Sentence Transformers for semantic search
│                 │  
├─────────────────┤
│  Data Layer     │  CSV file with petition data
│                 │  Cached embeddings for performance
└─────────────────┘
```

## 🛠️ Technical Stack

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **Sentence Transformers**: State-of-the-art models for semantic search
- **PyTorch**: Deep learning framework (CPU version)
- **Scikit-learn**: For cosine similarity calculations
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for running the API

### Frontend
- **Vanilla JavaScript**: No framework dependencies for simplicity
- **Chart.js**: Interactive charts for search analytics visualization
- **Modern CSS**: Clean, responsive design with CSS Grid and Flexbox
- **HTML5**: Semantic markup for accessibility
- **Google Fonts (Inter)**: Modern typography

### Data Storage
- **CSV file**: Petition data (~800KB)
- **Pickle cache**: Pre-computed embeddings (~10MB)
- **Local filesystem**: Simple storage for development

### AI Model
- **paraphrase-multilingual-MiniLM-L12-v2**: Lightweight but powerful model
  - Understands 50+ languages
  - Fast inference (perfect for real-time search)
  - Small size (120MB)
  - Excellent accuracy for semantic similarity

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- 2GB free disk space (for model and dependencies)

### Project Structure
```
petition-search/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application and routes
│   │   ├── models.py        # Pydantic data models
│   │   ├── search_engine.py # AI search logic
│   │   └── config.py        # Configuration settings
│   ├── data/
│   │   ├── petitions.csv       # Petition data (~800KB)
│   │   └── embeddings_cache.pkl # Cached AI embeddings (~10MB)
│   └── requirements.txt     # Python dependencies
└── frontend/
    ├── index.html          # Main HTML page
    ├── script.js           # JavaScript functionality
    └── style.css           # CSS styling
```

### Step 1: Clone or Download the Project
```bash
cd petition-search
```

### Step 2: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

This will install all necessary packages including:
- FastAPI for the web framework
- Sentence Transformers for AI-powered search
- Scikit-learn for similarity calculations
- Uvicorn for running the server
- And other dependencies

First run will download the AI model (~120MB).

## Step 3: Run the Backend & Frontend Server

### **💡 Quick Commands Reference:**

### 1. Activate environment
```bash
conda activate petition-search
```
### 2. Start backend
```bash
cd C:\Users\User\Desktop\petition-search\backend
python -m app.main
```
### 3. Start frontend (optional HTTP server)
```bash
cd C:\Users\User\Desktop\petition-search\frontend
python -m http.server 3000
```
### 4. Deactivate environment when done
```bash
conda deactivate
```


## 🎮 Usage

### Web Interface
1. Open the frontend in your browser
2. Enter a natural language query (e.g., "environmental protection")
3. Optionally set filters (state, minimum signatures, result limit)
4. Click Search or press Enter
5. View results ranked by relevance
6. Explore interactive analytics charts showing:
   - Query coverage (related vs unrelated petitions)
   - Top petitions by signatures
   - Status distribution (open/closed/rejected)

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation (Swagger UI)

### Example API Request
```bash
# Basic search
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "climate change", "limit": 5}'

# Search with analytics
curl -X POST "http://localhost:8000/api/search/analytics" \
  -H "Content-Type: application/json" \
  -d '{"query": "climate change", "limit": 10}'
```

## 💡 How It Works

### 1. Data Loading
- Reads petition data from CSV file
- Cleans and preprocesses text for optimal embedding quality

### 2. Embedding Generation
- Converts each petition title to a vector representation
- Vectors capture semantic meaning, not just keywords
- Embeddings are cached to disk for fast subsequent starts

### 3. Search Process
1. User enters a natural language query
2. Query is converted to an embedding vector
3. Cosine similarity calculated between query and all petitions
4. Results ranked by similarity score
5. Filters applied (if any)
6. Top results returned with metadata

### 4. Fallback Strategy
If semantic search fails, system falls back to keyword matching to ensure users always get results.

## 🎯 Addressing Tech Test Requirements

### Query Matching ✅
- **Semantic understanding** using state-of-the-art Sentence Transformers
- **Cosine similarity** for accurate relevance scoring
- **Keyword fallback** ensures results even without embeddings

### Security & Safety ✅
- **Input validation**: Query length limits, sanitization
- **CORS configuration**: Controlled cross-origin access
- **Rate limiting headers**: Prevent API abuse
- **Error handling**: Graceful degradation, no stack traces exposed
- **XSS prevention**: HTML escaping in frontend

### Scalability Considerations ✅
```python
# Current approach (Prototype - 3-4 hours)
- Local embeddings storage
- In-memory search
- CSV data source
- Single server instance

# Production improvements (documented in code):
- Vector database (Pinecone/Weaviate)
- Redis caching layer
- PostgreSQL for petition data
- Horizontal scaling with load balancer
- Background job queue for embedding generation
- CDN for frontend assets
```

### Result Presentation ✅
- **Relevance scores**: Shown as match percentage
- **Clear ranking**: Results numbered by relevance
- **Rich metadata**: Status badges, signature counts
- **Responsive design**: Works on all devices
- **Smooth UX**: Loading states, error messages

### Reducing Noise ✅
- **Similarity threshold**: Can filter low-relevance results
- **State filtering**: Open/closed petitions
- **Signature filtering**: Find popular petitions
- **Clean text processing**: Removes special characters

## 📊 Performance Metrics

- **First search**: ~2-3 seconds (including model loading)
- **Subsequent searches**: ~100-200ms
- **Embedding generation**: ~5 seconds for 1000 petitions
- **Cache size**: ~5MB for 1000 petitions
- **Memory usage**: ~500MB with model loaded

## 🔄 Trade-offs & Decisions

### Why Sentence Transformers?
- ✅ Better semantic understanding than keyword search
- ✅ Pre-trained models work out of the box
- ✅ Fast enough for real-time search
- ❌ Requires more memory than simple text matching

### Why Local Storage?
- ✅ Simple to implement in 3-4 hours
- ✅ No external dependencies
- ✅ Fast for small datasets
- ❌ Won't scale to millions of records

### Why FastAPI?
- ✅ Modern, fast, automatic API documentation
- ✅ Great for building APIs quickly
- ✅ Type hints and validation built-in
- ✅ Production-ready with async support

## 🚀 Production Improvements

If given more time, here's what I would add:

### Immediate (Next 4 hours)
- [ ] Add comprehensive test suite (pytest)
- [ ] Implement actual rate limiting with Redis
- [ ] Add database support (PostgreSQL)
- [ ] Create Docker containers
- [ ] Add logging to file with rotation

### Short-term (1 week)
- [ ] Vector database integration (Pinecone/Weaviate)
- [ ] Authentication and API keys
- [ ] Advanced filtering (date ranges, categories)
- [ ] Search analytics dashboard
- [ ] A/B testing framework for model comparison

### Long-term (1 month)
- [ ] Fine-tune model on petition-specific data
- [ ] Multi-language support
- [ ] Query suggestion/autocomplete
- [ ] User feedback loop for improving results
- [ ] Distributed architecture with microservices

## 🧪 Testing

### Manual Testing Checklist
- [x] Search with various query types
- [x] Test all filters work correctly
- [x] Check error handling (empty query, long query)
- [x] Verify responsive design on mobile
- [x] Test API endpoints directly
- [x] Check performance with different result limits

### Sample Test Queries
1. "climate change" - Should find environmental petitions
2. "education and schools" - Should find education-related petitions
3. "NHS healthcare" - Should find health-related petitions
4. "askjdhaksjdh" - Should return no results gracefully
5. "" (empty) - Should show error message

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/api/search` | POST | Main search endpoint |
| `/api/search/analytics` | POST | Advanced search analytics with charts data |
| `/api/stats` | GET | Dataset statistics |
| `/api/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

### Search Request Body
```json
{
  "query": "climate change",
  "limit": 10
}
```

### Search Response
```json
{
  "query": "climate change",
  "results": [
    {
      "title": "Petition title",
      "url": "https://petition.parliament.uk/...",
      "state": "open",
      "signatures": 12345
    }
  ],
  "count": 5
}
```

## 🤝 Contributing

This was built for a tech test, but feel free to fork and improve!

### Areas for Contribution
- Better embedding models
- More sophisticated ranking algorithms
- Additional filters and search options
- Performance optimizations
- UI/UX improvements

## 📄 License

MIT License - Feel free to use this code for learning purposes.

## 🙏 Acknowledgments

- Sentence Transformers team for the amazing models
- FastAPI team for the excellent framework
- The open-source community for inspiration

---
