"""
Team Normalization Service
==========================
Provides standard normalization for team names to facilitate O(N) matching
between different data providers (e.g., ESPN and The Odds API).
"""

import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class TeamNormalizationService:
    """Service to normalize and match team names efficiently."""
    
    def __init__(self):
        # Common suffixes to ignore during normalization
        self.ignored_suffixes = [
            " fc", " sc", " united", " city", " real", " atletico", 
            " inter", " ac", " as", " sv", " vfb"
        ]
        
        # Manual overrides for difficult matches
        # Format: "normalized_name": "canonical_id"
        self.manual_overrides = {
            "man utd": "manchester united",
            "man city": "manchester city",
            # Add more as discovered
        }
    
    def normalize_name(self, name: str) -> str:
        """
        Normalize a team name for consistent matching.
        Strategy:
        1. Lowercase
        2. Remove special characters
        3. Strip extra whitespace
        """
        if not name:
            return ""
            
        # Lowercase
        normalized = name.lower()
        
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Strip extra whitespace
        normalized = " ".join(normalized.split())
        
        return normalized
    
    def create_lookup_map(self, items: List[Dict[str, Any]], name_key: str = 'home_team') -> Dict[str, Dict[str, Any]]:
        """
        Create a hash map for O(1) lookups from a list of dictionaries.
        Returns: {normalized_name: original_item}
        """
        lookup = {}
        for item in items:
            name = item.get(name_key)
            if name:
                norm_name = self.normalize_name(name)
                lookup[norm_name] = item
                
                # Also index alternate keys if present (e.g., shortName)
                if 'shortName' in item:
                    norm_short = self.normalize_name(item['shortName'])
                    if norm_short:
                        lookup[norm_short] = item
                        
        return lookup
    
    def find_match(self, name: str, lookup_map: Dict[str, Any]) -> Optional[Any]:
        """
        Find a match in the lookup map using the normalized name.
        Complexity: O(1)
        """
        norm_name = self.normalize_name(name)
        
        # Direct match
        if norm_name in lookup_map:
            return lookup_map[norm_name]
            
        # Check overrides
        if norm_name in self.manual_overrides:
            override_name = self.manual_overrides[norm_name]
            if override_name in lookup_map:
                return lookup_map[override_name]
        
        # Fallback: Check for partial matches (more expensive, basically the old fuzzy match but optimized)
        # We try to avoid this by having good normalization, but here we can check if 
        # the key is a substring of the target or vice versa for safety
        # NOTE: For true O(N) total performance, we should avoid iterating keys here.
        # But failing a hash lookup is fast.
        
        return None

# Global instance
normalization_service = TeamNormalizationService()
