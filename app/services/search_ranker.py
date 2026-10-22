from typing import List, Dict, Any
from rapidfuzz import fuzz

class SearchRanker:
    """
    Ranks the search results from ShamelaScraper using the normalized LLM outputs
    scoring formula:
    final_score = (fts_score * 0.6) + (llm_confidence * 0.2) + (exact_title_match * 0.1) + (exact_author_match * 0.1)
    """
    @staticmethod
    def rank_results(results: List[Dict], llm_json: Dict[str, Any]) -> List[Dict]:
        if not results or not llm_json:
            return results
            
        normalized_title = llm_json.get("normalized_title", "")
        arabic_title = llm_json.get("arabic_title", "")
        alternative_spellings = llm_json.get("alternative_spellings", [])
        
        # Build set of target titles for fuzzy matching
        target_titles = [normalized_title, arabic_title] + alternative_spellings
        target_titles = [t for t in target_titles if t]
        
        # Core keywords (Arabic) for strict filtering/boosting
        core_keywords = []
        if arabic_title:
            core_keywords = [k for k in arabic_title.split() if len(k) > 2] # Avoid very short words

        for r in results:
            res_title = r.get("judul_arab", "")
            res_author = r.get("penulis_arab", "")
            
            # 1. Fuzzy Title Score (using token_set_ratio for partial matches)
            title_score = 0
            if target_titles:
                # token_set_ratio is GREAT for partial matches like "Muslim" in "Syarah Muslim"
                scores = [fuzz.token_set_ratio(t, res_title) for t in target_titles]
                title_score = max(scores) / 100.0
            
            # 2. Keyword Containment Bonus (Strict)
            keyword_bonus = 0.0
            if core_keywords:
                matches = 0
                for k in core_keywords:
                    if k in res_title:
                        matches += 1
                keyword_bonus = (matches / len(core_keywords)) * 0.3 # Max 0.3 bonus
            
            # 3. Author similarity
            normalized_author = llm_json.get("normalized_author", "")
            auth_score = 0
            if normalized_author:
                auth_score = fuzz.token_set_ratio(normalized_author, res_author) / 100.0
            
            # 4. Exact match huge bonus
            exact_title = 0.5 if any(t == res_title.strip() for t in target_titles) else 0.0
            
            # Final calculation
            # We favor title_score and keyword_bonus heavily
            final_score = (title_score * 0.5) + (keyword_bonus * 0.3) + (auth_score * 0.1) + exact_title
            
            # If the title has absolutely NOTHING to do with the target, penalize
            if title_score < 0.2 and keyword_bonus == 0:
                final_score *= 0.1

            r["_score"] = final_score
            
        # Sort descending by _score
        ranked = sorted(results, key=lambda x: x.get("_score", 0), reverse=True)
        return ranked
