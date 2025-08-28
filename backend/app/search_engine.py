"""
Core search engine implementation using Sentence Transformers.
This is where the AI magic happens - converting text to vectors and finding similarities!

The approach:
1. Load petition data from CSV
2. Convert petition text to embeddings (vector representations)
3. When user searches, convert their query to embedding
4. Find most similar petitions using cosine similarity
5. Return ranked results

Author: Junior Developer
"""

import os
import csv
import torch
import pickle
import logging
import time
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

logger = logging.getLogger(__name__)


class PetitionSearchEngine:
    """
    Main search engine that handles semantic search for petitions.
    Uses Sentence Transformers to understand meaning, not just keywords!
    """
    
    def __init__(self, csv_path: str, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2', 
                 embeddings_cache_path: str = 'embeddings_cache.pkl'):
        """
        Initialize the search engine.
        
        Args:
            csv_path: Path to the CSV file containing petition data
            model_name: Name of the sentence transformer model to use
            embeddings_cache_path: Path to cache embeddings (speeds up subsequent starts)
        """
        self.csv_path = csv_path
        self.embeddings_cache_path = embeddings_cache_path
        self.embeddings_loaded = False
        
        # Load the AI model - this understands language meaning
        logger.info(f"Loading sentence transformer model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
        
        # Load petition data and create embeddings
        self.petitions = []
        self.embeddings = None
        self._load_data()
        self._prepare_embeddings()
    
    def _load_data(self):
        """
        Load petition data from CSV file.
        Handles the specific format: title, URL, state, signatures
        """
        logger.info(f"Loading petition data from {self.csv_path}")
        
        if not os.path.exists(self.csv_path):
            # Create sample data if CSV doesn't exist
            logger.warning("CSV file not found, creating sample data...")
            self._create_sample_data()
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                # Try to detect if there's a header
                first_line = file.readline()
                file.seek(0)  # Go back to start
                
                # Check if first line looks like a header
                has_header = 'http' not in first_line.lower()
                
                if has_header:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Try different possible column names
                        title = row.get('title') or row.get('petition') or row.get('text') or ''
                        url = row.get('url') or row.get('link') or ''
                        state = row.get('state') or row.get('status') or 'unknown'
                        
                        # Handle signatures - might be string with commas
                        sig_str = row.get('signatures') or row.get('signature_count') or '0'
                        signatures = int(sig_str.replace(',', ''))
                        
                        self.petitions.append({
                            'title': self._clean_text(title),
                            'url': url,
                            'state': state.lower(),
                            'signatures': signatures
                        })
                else:
                    # No header, parse as space-separated values
                    file.seek(0)
                    for line in file:
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            # Assume format: title... url state signatures
                            # Find URL in the line
                            url_pattern = r'https?://[^\s]+'
                            url_match = re.search(url_pattern, line)
                            
                            if url_match:
                                url = url_match.group()
                                url_index = line.index(url)
                                
                                # Everything before URL is title
                                title = line[:url_index].strip()
                                
                                # Everything after URL is state and signatures
                                after_url = line[url_index + len(url):].strip().split()
                                state = after_url[0] if after_url else 'unknown'
                                signatures = int(after_url[1]) if len(after_url) > 1 else 0
                                
                                self.petitions.append({
                                    'title': self._clean_text(title),
                                    'url': url,
                                    'state': state.lower(),
                                    'signatures': signatures
                                })
            
            logger.info(f"Loaded {len(self.petitions)} petitions successfully")
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            # Create sample data as fallback
            self._create_sample_data()
    
    def _clean_text(self, text: str) -> str:
        """
        Clean petition text for better embedding quality.
        Removes extra whitespace, special characters, etc.
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Limit length to prevent memory issues
        if len(text) > 500:
            text = text[:500] + '...'
        
        return text
    
    def _create_sample_data(self):
        """
        Create sample petition data for testing.
        This ensures the system works even without real data.
        """
        logger.info("Creating sample petition data...")
        
        sample_petitions = [
            {
                'title': 'Increase funding for renewable energy research and development',
                'url': 'https://petition.parliament.uk/petitions/700001',
                'state': 'open',
                'signatures': 45678
            },
            {
                'title': 'Ban single-use plastics in all UK supermarkets by 2026',
                'url': 'https://petition.parliament.uk/petitions/700002',
                'state': 'open',
                'signatures': 123456
            },
            {
                'title': 'Improve mental health support in schools',
                'url': 'https://petition.parliament.uk/petitions/700003',
                'state': 'open',
                'signatures': 87234
            },
            {
                'title': 'Make climate change education mandatory in schools',
                'url': 'https://petition.parliament.uk/petitions/700004',
                'state': 'closed',
                'signatures': 234567
            },
            {
                'title': 'Fund reconstruction surgery and psychosexual therapy for FGM survivors',
                'url': 'https://petition.parliament.uk/petitions/700005',
                'state': 'closed',
                'signatures': 939
            },
            {
                'title': 'Reduce university tuition fees to £3000 per year',
                'url': 'https://petition.parliament.uk/petitions/700006',
                'state': 'open',
                'signatures': 567890
            },
            {
                'title': 'Protect green belt land from housing development',
                'url': 'https://petition.parliament.uk/petitions/700007',
                'state': 'open',
                'signatures': 34567
            },
            {
                'title': 'Increase NHS funding by 10% annually',
                'url': 'https://petition.parliament.uk/petitions/700008',
                'state': 'closed',
                'signatures': 456789
            },
            {
                'title': 'Ban the sale of fireworks to the public',
                'url': 'https://petition.parliament.uk/petitions/700009',
                'state': 'open',
                'signatures': 23456
            },
            {
                'title': 'Implement a four-day working week pilot scheme',
                'url': 'https://petition.parliament.uk/petitions/700010',
                'state': 'open',
                'signatures': 98765
            }
        ]
        
        self.petitions = sample_petitions
        
        # Save to CSV for next time
        try:
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['title', 'url', 'state', 'signatures'])
                writer.writeheader()
                writer.writerows(sample_petitions)
            logger.info(f"Sample data saved to {self.csv_path}")
        except Exception as e:
            logger.warning(f"Could not save sample data: {e}")
    
    def _prepare_embeddings(self):
        """
        Create embeddings for all petitions.
        This converts text to vectors that capture meaning.
        
        Uses caching to speed up subsequent starts.
        """
        cache_file = self.embeddings_cache_path
        
        # Try to load cached embeddings first (much faster!)
        if os.path.exists(cache_file):
            try:
                logger.info("Loading cached embeddings...")
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    
                # Check if cached data matches current petitions
                if len(cached_data['petitions']) == len(self.petitions):
                    # Simple check - in production we'd use a hash
                    self.embeddings = cached_data['embeddings']
                    self.embeddings_loaded = True
                    logger.info("Loaded embeddings from cache successfully")
                    return
            except Exception as e:
                logger.warning(f"Could not load cached embeddings: {e}")
        
        # Generate new embeddings
        logger.info("Generating embeddings for all petitions...")
        start_time = time.time()
        
        # Extract just the titles for embedding
        petition_texts = [p['title'] for p in self.petitions]
        
        # Convert to embeddings (this is the AI part!)
        # The model understands meaning and creates vectors
        self.embeddings = self.model.encode(petition_texts, show_progress_bar=True)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Generated embeddings in {elapsed_time:.2f} seconds")
        
        # Cache the embeddings for next time
        try:
            cache_data = {
                'petitions': self.petitions,
                'embeddings': self.embeddings
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.info("Cached embeddings for future use")
        except Exception as e:
            logger.warning(f"Could not cache embeddings: {e}")
        
        self.embeddings_loaded = True
    
    def search(self, query: str, top_k: int = 10, 
               state_filter: Optional[str] = None,
               min_signatures: Optional[int] = None,
               include_similarity_score: bool = True) -> List[Dict]:
        """
        Perform semantic search on petitions.
        
        This is the main search function that:
        1. Converts the query to an embedding
        2. Finds similar petition embeddings
        3. Ranks and filters results
        
        Args:
            query: Natural language search query
            top_k: Number of results to return
            state_filter: Filter by petition state (open/closed)
            min_signatures: Minimum signature count
            include_similarity_score: Whether to include similarity scores
        
        Returns:
            List of matching petitions ranked by relevance
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not self.embeddings_loaded:
            raise RuntimeError("Embeddings not loaded. Search engine not ready.")
        
        logger.info(f"Searching for: '{query}'")
        start_time = time.time()
        
        # Convert query to embedding (vector)
        query_embedding = self.model.encode([query])
        
        # Calculate similarity between query and all petitions
        # Cosine similarity measures how similar two vectors are (0-1)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Create results with similarity scores
        results = []
        for idx, similarity in enumerate(similarities):
            petition = self.petitions[idx].copy()
            
            # Apply filters
            if state_filter and petition['state'] != state_filter.lower():
                continue
            if min_signatures and petition['signatures'] < min_signatures:
                continue
            
            # Add similarity score
            if include_similarity_score:
                petition['similarity_score'] = float(similarity)
            
            results.append(petition)
        
        # Sort by similarity score (highest first)
        results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        # Add ranking
        for i, result in enumerate(results[:top_k]):
            result['rank'] = i + 1
        
        # Get top k results
        results = results[:top_k]
        
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
        logger.info(f"Search completed in {elapsed_time:.2f}ms, found {len(results)} results")
        
        return results
    
    def keyword_fallback_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Fallback to simple keyword search if semantic search fails.
        This ensures we always return something, even without AI.
        """
        logger.info(f"Using keyword fallback for: '{query}'")
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        for petition in self.petitions:
            title_lower = petition['title'].lower()
            title_words = set(title_lower.split())
            
            # Calculate simple word overlap score
            common_words = query_words.intersection(title_words)
            if common_words:
                score = len(common_words) / len(query_words)
                result = petition.copy()
                result['similarity_score'] = score
                results.append(result)
        
        # Sort by score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Add ranking
        for i, result in enumerate(results[:top_k]):
            result['rank'] = i + 1
        
        return results[:top_k]
    
    def get_all_petitions(self, offset: int = 0, limit: int = 20, 
                          state_filter: Optional[str] = None) -> List[Dict]:
        """
        Get all petitions with pagination support.
        Used for browsing without searching.
        """
        filtered = self.petitions
        
        if state_filter:
            filtered = [p for p in filtered if p['state'] == state_filter.lower()]
        
        return filtered[offset:offset + limit]
    
    def get_petition_count(self, state_filter: Optional[str] = None) -> int:
        """
        Get the total count of petitions.
        """
        if state_filter:
            return sum(1 for p in self.petitions if p['state'] == state_filter.lower())
        return len(self.petitions)
    
    def get_statistics(self) -> Dict:
        """
        Calculate statistics about the petition dataset.
        Helps users understand what data is available.
        """
        if not self.petitions:
            return {
                'total_petitions': 0,
                'open_petitions': 0,
                'closed_petitions': 0,
                'total_signatures': 0,
                'average_signatures': 0
            }
        
        open_count = sum(1 for p in self.petitions if p['state'] == 'open')
        closed_count = sum(1 for p in self.petitions if p['state'] == 'closed')
        total_signatures = sum(p['signatures'] for p in self.petitions)
        
        # Find most signed petition
        most_signed = max(self.petitions, key=lambda x: x['signatures'])
        
        return {
            'total_petitions': len(self.petitions),
            'open_petitions': open_count,
            'closed_petitions': closed_count,
            'total_signatures': total_signatures,
            'average_signatures': total_signatures / len(self.petitions),
            'most_signed': most_signed
        }
    
    def is_ready(self) -> bool:
        """
        Check if the search engine is ready to handle queries.
        """
        return self.embeddings_loaded and len(self.petitions) > 0
