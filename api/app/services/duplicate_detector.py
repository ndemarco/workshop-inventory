"""
Duplicate Detection Service for Phase 3

This service identifies similar or duplicate items before they are added to the inventory.
It uses multiple similarity metrics:
1. Levenshtein distance for string similarity
2. Specification matching (extracted specs)
3. Tag overlap
4. Category matching

The goal is to prevent accidental duplicates while allowing intentional variations.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from difflib import SequenceMatcher

from app.services.spec_parser import SpecificationParser, ParsedSpec


@dataclass
class DuplicateMatch:
    """Represents a potential duplicate item"""
    item_id: int
    item_name: str
    item_description: str
    similarity_score: float  # 0.0 to 1.0
    match_reasons: List[str]
    differences: List[str]
    locations: List[Dict]  # Where the item is stored
    quantity: int
    unit: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'item_id': self.item_id,
            'item_name': self.item_name,
            'item_description': self.item_description,
            'similarity_score': round(self.similarity_score, 2),
            'match_reasons': self.match_reasons,
            'differences': self.differences,
            'locations': self.locations,
            'quantity': self.quantity,
            'unit': self.unit
        }


class DuplicateDetector:
    """Detect duplicate or similar items in inventory"""
    
    def __init__(self):
        self.spec_parser = SpecificationParser()
        # Minimum similarity threshold to be considered a potential duplicate
        self.similarity_threshold = 0.70
    
    def find_similar(
        self, 
        name: str, 
        description: str,
        category: Optional[str],
        tags: Optional[str],
        existing_items: List[Dict],
        threshold: Optional[float] = None
    ) -> List[DuplicateMatch]:
        """
        Find similar items in the existing inventory
        
        Args:
            name: Name of the new item
            description: Description of the new item
            category: Category of the new item
            tags: Comma-separated tags
            existing_items: List of existing items to compare against
            threshold: Optional custom similarity threshold (0.0-1.0)
            
        Returns:
            List of DuplicateMatch objects, sorted by similarity (highest first)
        """
        if threshold is None:
            threshold = self.similarity_threshold
        
        # Parse the new item's specs
        new_specs = self.spec_parser.parse(description, name)
        new_tags = self._parse_tags(tags)
        
        matches = []
        
        for existing in existing_items:
            similarity = self.calculate_similarity(
                name, description, category, new_tags, new_specs,
                existing, threshold
            )
            
            if similarity['score'] >= threshold:
                # Get locations for this item
                locations = self._format_locations(existing.get('locations', []))
                
                match = DuplicateMatch(
                    item_id=existing['id'],
                    item_name=existing['name'],
                    item_description=existing.get('description', ''),
                    similarity_score=similarity['score'],
                    match_reasons=similarity['reasons'],
                    differences=similarity['differences'],
                    locations=locations,
                    quantity=existing.get('quantity', 0),
                    unit=existing.get('unit', 'pieces')
                )
                matches.append(match)
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return matches
    
    def calculate_similarity(
        self,
        name: str,
        description: str,
        category: Optional[str],
        tags: List[str],
        parsed_specs: ParsedSpec,
        existing_item: Dict,
        threshold: float
    ) -> Dict[str, any]:
        """
        Calculate similarity score between new item and existing item
        
        Returns dict with:
        - score: float (0.0 to 1.0)
        - reasons: List[str] explaining why it's similar
        - differences: List[str] explaining differences
        """
        score = 0.0
        reasons = []
        differences = []
        
        existing_name = existing_item.get('name', '')
        existing_desc = existing_item.get('description', '')
        existing_category = existing_item.get('category', '')
        existing_tags = self._parse_tags(existing_item.get('tags', ''))
        
        # 1. Name similarity (30% weight)
        name_sim = self._string_similarity(name.lower(), existing_name.lower())
        if name_sim > 0.8:
            score += 0.30 * name_sim
            reasons.append(f"Very similar name ({int(name_sim * 100)}% match)")
        elif name_sim > 0.6:
            score += 0.30 * name_sim
            reasons.append(f"Similar name ({int(name_sim * 100)}% match)")
        else:
            differences.append(f"Different names: '{name}' vs '{existing_name}'")
        
        # 2. Description similarity (25% weight)
        desc_sim = self._string_similarity(description.lower(), existing_desc.lower())
        if desc_sim > 0.7:
            score += 0.25 * desc_sim
            reasons.append(f"Similar description ({int(desc_sim * 100)}% match)")
        elif desc_sim > 0.5:
            score += 0.15 * desc_sim
        else:
            differences.append("Different descriptions")
        
        # 3. Category match (10% weight)
        if category and existing_category:
            if category.lower() == existing_category.lower():
                score += 0.10
                reasons.append(f"Same category: {category}")
            else:
                differences.append(f"Different categories: {category} vs {existing_category}")
        
        # 4. Tag overlap (15% weight)
        if tags and existing_tags:
            tag_overlap = len(set(tags) & set(existing_tags))
            tag_union = len(set(tags) | set(existing_tags))
            if tag_union > 0:
                tag_score = tag_overlap / tag_union
                if tag_score > 0.5:
                    score += 0.15 * tag_score
                    common_tags = set(tags) & set(existing_tags)
                    reasons.append(f"Common tags: {', '.join(list(common_tags)[:3])}")
        
        # 5. Specification match (20% weight)
        # Parse existing item specs
        existing_specs = self.spec_parser.parse(existing_desc, existing_name)
        
        spec_similarity = self._compare_specs(parsed_specs, existing_specs)
        if spec_similarity['score'] > 0:
            score += 0.20 * spec_similarity['score']
            if spec_similarity['matches']:
                reasons.extend(spec_similarity['matches'])
            if spec_similarity['differences']:
                differences.extend(spec_similarity['differences'])
        
        return {
            'score': min(1.0, score),
            'reasons': reasons,
            'differences': differences if differences else ['No significant differences found']
        }
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate string similarity using SequenceMatcher
        Returns value between 0.0 and 1.0
        """
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _levenshtein_distance(self, str1: str, str2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(str1) < len(str2):
            return self._levenshtein_distance(str2, str1)
        
        if len(str2) == 0:
            return len(str1)
        
        previous_row = range(len(str2) + 1)
        for i, c1 in enumerate(str1):
            current_row = [i + 1]
            for j, c2 in enumerate(str2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _parse_tags(self, tags_str: Optional[str]) -> List[str]:
        """Parse comma-separated tags string into list"""
        if not tags_str:
            return []
        return [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
    
    def _compare_specs(self, specs1: ParsedSpec, specs2: ParsedSpec) -> Dict:
        """
        Compare parsed specifications between two items
        
        Returns dict with:
        - score: float (0.0 to 1.0)
        - matches: List[str] of matching specs
        - differences: List[str] of different specs
        """
        if not specs1.specs or not specs2.specs:
            return {'score': 0.0, 'matches': [], 'differences': []}
        
        score = 0.0
        matches = []
        differences = []
        
        # Compare categories
        if specs1.category and specs2.category:
            if specs1.category == specs2.category:
                score += 0.3
                matches.append(f"Same type: {specs1.category}")
            else:
                differences.append(f"Different types: {specs1.category} vs {specs2.category}")
                return {'score': score, 'matches': matches, 'differences': differences}
        
        # Compare individual spec values
        common_keys = set(specs1.specs.keys()) & set(specs2.specs.keys())
        
        if not common_keys:
            return {'score': score, 'matches': matches, 'differences': differences}
        
        matching_specs = 0
        total_specs = len(common_keys)
        
        for key in common_keys:
            val1 = specs1.specs[key]
            val2 = specs2.specs[key]
            
            if val1 == val2:
                matching_specs += 1
                # Don't add every match to reasons (too verbose)
                if key in ['thread_size', 'package', 'resistance_str', 'capacitance_str']:
                    matches.append(f"Same {key}: {val1}")
            else:
                differences.append(f"Different {key}: {val1} vs {val2}")
        
        if total_specs > 0:
            spec_match_ratio = matching_specs / total_specs
            score += 0.7 * spec_match_ratio
        
        return {
            'score': score,
            'matches': matches,
            'differences': differences
        }
    
    def _format_locations(self, locations: List) -> List[Dict]:
        """Format location information for display"""
        formatted = []
        for loc in locations:
            if isinstance(loc, dict):
                # Already formatted
                formatted.append(loc)
            else:
                # It's a Location object
                formatted.append({
                    'module': getattr(loc.level.module, 'name', 'Unknown') if hasattr(loc, 'level') else 'Unknown',
                    'level': getattr(loc.level, 'level_number', '?') if hasattr(loc, 'level') else '?',
                    'location': f"{loc.row}{loc.column}" if hasattr(loc, 'row') else 'Unknown',
                    'quantity': getattr(loc, 'quantity', 0) if hasattr(loc, 'quantity') else 0
                })
        return formatted
    
    def suggest_merge(self, item1_id: int, item2_id: int) -> Dict:
        """
        Suggest how to merge two duplicate items
        
        Returns a dict with:
        - merged_name: str
        - merged_description: str
        - merged_locations: List of locations
        - total_quantity: int
        - suggestions: List[str] of merge recommendations
        """
        # This is a placeholder for future implementation
        # In a real system, this would:
        # 1. Fetch both items from DB
        # 2. Combine their locations
        # 3. Sum quantities
        # 4. Merge tags
        # 5. Suggest a unified description
        
        return {
            'merged_name': 'To be implemented',
            'merged_description': 'To be implemented',
            'merged_locations': [],
            'total_quantity': 0,
            'suggestions': [
                'Combine quantities',
                'Keep all locations',
                'Merge unique tags',
                'Use more detailed description'
            ]
        }


# Utility function for quick similarity check
def quick_similarity_check(str1: str, str2: str) -> float:
    """Quick string similarity check without full parsing"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
