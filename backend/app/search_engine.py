# search engine using AI - this is the main part that does the smart searching
# I followed some tutorials about sentence transformers and vector search

import csv
import pickle
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class PetitionSearchEngine:
    
    def __init__(self, csv_path, model_name, cache_path):
        self.csv_path = csv_path
        self.cache_path = cache_path
        
        # load the AI model
        print("Loading AI model...")
        self.model = SentenceTransformer(model_name)
        
        # load petition data
        self.petitions = []
        self._load_petitions()
        self._make_embeddings()
    
    def _load_petitions(self):
        # load petitions from the CSV file
        print("Loading petition data...")
        with open(self.csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.petitions.append({
                    'title': row['title'],
                    'url': row['url'],
                    'state': row['state'],
                    'signatures': int(row['signatures'])
                })
    
    def _make_embeddings(self):
        # try to load cached embeddings first
        if os.path.exists(self.cache_path):
            print("Loading cached embeddings...")
            with open(self.cache_path, 'rb') as f:
                cached_data = pickle.load(f)
                if isinstance(cached_data, dict) and 'embeddings' in cached_data:
                    self.embeddings = cached_data['embeddings']
                    print("Loaded embeddings from cache")
                    return
                else:
                    # old cache format, just use the data directly
                    self.embeddings = cached_data
                    print("Loaded embeddings from cache (old format)")
                    return
        
        # create embeddings for all petition titles
        print("Creating embeddings...")
        texts = [p['title'] for p in self.petitions]
        self.embeddings = self.model.encode(texts)
        print(f"Created embeddings for {len(texts)} petitions")
        
        # save embeddings to cache
        print("Saving embeddings to cache...")
        cache_data = {
            'embeddings': self.embeddings,
            'petition_count': len(self.petitions)
        }
        with open(self.cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
        print("Embeddings cached successfully")
    
    def search(self, query, limit=10):
        # convert query to embedding
        query_embedding = self.model.encode([query])
        
        # find similar petitions
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # create results
        results = []
        for i, similarity in enumerate(similarities):
            results.append({
                'title': self.petitions[i]['title'],
                'url': self.petitions[i]['url'],
                'state': self.petitions[i]['state'],
                'signatures': self.petitions[i]['signatures']
            })
        
        # sort by similarity and return top results
        results = sorted(zip(results, similarities), key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:limit]]
    
    def get_search_analytics(self, query, similarity_threshold=0.3):
        # convert query to embedding
        query_embedding = self.model.encode([query])
        
        # find similar petitions
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # find petitions above similarity threshold
        related_petitions = []
        for i, similarity in enumerate(similarities):
            if similarity >= similarity_threshold:
                petition = self.petitions[i].copy()
                petition['similarity'] = float(similarity)
                related_petitions.append(petition)
        
        # sort by similarity
        related_petitions.sort(key=lambda x: x['similarity'], reverse=True)
        
        # calculate statistics
        total_petitions = len(self.petitions)
        related_count = len(related_petitions)
        
        # percentage of related vs total
        percentage_related = (related_count / total_petitions) * 100 if total_petitions > 0 else 0
        
        # top 10 by signatures
        top_by_signatures = sorted(related_petitions, key=lambda x: x['signatures'], reverse=True)[:10]
        
        # status counts for related petitions
        open_count = len([p for p in related_petitions if p['state'] == 'open'])
        closed_count = len([p for p in related_petitions if p['state'] == 'closed'])
        rejected_count = len([p for p in related_petitions if p['state'] == 'rejected'])
        
        return {
            'total_petitions': total_petitions,
            'related_petitions': related_count,
            'percentage_related': round(percentage_related, 2),
            'similarity_threshold': similarity_threshold,
            'pie_chart_data': {
                'related': related_count,
                'unrelated': total_petitions - related_count
            },
            'top_10_signatures': [
                {
                    'title': p['title'][:45] + '...' if len(p['title']) > 45 else p['title'],
                    'signatures': p['signatures']
                } for p in top_by_signatures
            ],
            'status_breakdown': {
                'open': open_count,
                'closed': closed_count,
                'rejected': rejected_count
            }
        }
