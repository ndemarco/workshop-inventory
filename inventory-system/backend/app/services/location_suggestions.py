"""
Location Suggestion Service
Provides intelligent recommendations for where to store items
"""

from typing import List, Dict, Tuple
from app.models import Location, Item, ItemLocation, db
from sqlalchemy import func, and_


class LocationSuggestion:
    """Represents a suggested location with scoring and reasoning"""
    
    def __init__(self, location: Location, score: float, reasons: List[str]):
        self.location = location
        self.score = score
        self.reasons = reasons
    
    def to_dict(self):
        return {
            'location': self.location.to_dict(),
            'score': round(self.score, 2),
            'reasons': self.reasons
        }


class LocationSuggestionService:
    """Service for generating smart location suggestions"""
    
    @staticmethod
    def suggest_locations(
        item_category: str = None,
        item_type: str = None,
        item_tags: List[str] = None,
        width_mm: float = None,
        height_mm: float = None,
        depth_mm: float = None,
        limit: int = 5
    ) -> List[LocationSuggestion]:
        """
        Generate smart location suggestions based on item characteristics
        
        Args:
            item_category: Category of the item (e.g., 'Fasteners', 'Electronics')
            item_type: Type of item (e.g., 'solid', 'liquid', 'smd_component')
            item_tags: List of tags for the item
            width_mm, height_mm, depth_mm: Item dimensions
            limit: Maximum number of suggestions to return
        
        Returns:
            List of LocationSuggestion objects, sorted by score (highest first)
        """
        # Get all locations with their current items
        locations = Location.query.all()
        suggestions = []
        
        for location in locations:
            score = 0.0
            reasons = []
            
            # Score 1: Empty locations get base points
            item_count = len(location.item_locations)
            if item_count == 0:
                score += 10
                reasons.append("Empty location - ready for use")
            elif item_count < 3:
                score += 5
                reasons.append(f"Has space ({item_count} item(s) stored)")
            else:
                score += 1
                reasons.append(f"Occupied ({item_count} item(s) stored)")
            
            # Score 2: Category matching - items with same category
            if item_category:
                category_matches = 0
                for item_loc in location.item_locations:
                    if item_loc.item.category == item_category:
                        category_matches += 1
                
                if category_matches > 0:
                    score += category_matches * 15
                    reasons.append(f"Similar category items here ({category_matches} {item_category} items)")
            
            # Score 3: Item type matching
            if item_type:
                # Prefer compatible location types
                location_type_scores = {
                    'solid': ['general', 'small_box', 'medium_bin', 'large_bin'],
                    'liquid': ['liquid_container'],
                    'smd_component': ['smd_container', 'small_box'],
                    'bulk': ['large_bin', 'bulk_storage']
                }
                
                compatible_types = location_type_scores.get(item_type, ['general'])
                if location.location_type in compatible_types:
                    score += 8
                    reasons.append(f"Compatible storage type ({location.location_type})")
            
            # Score 4: Size matching (if dimensions provided)
            if all([width_mm, height_mm, depth_mm, 
                    location.width_mm, location.height_mm, location.depth_mm]):
                # Check if item fits
                fits_width = width_mm <= location.width_mm
                fits_height = height_mm <= location.height_mm
                fits_depth = depth_mm <= location.depth_mm
                
                if fits_width and fits_height and fits_depth:
                    # Calculate how well it fits (prefer snug fit over huge location)
                    volume_item = width_mm * height_mm * depth_mm
                    volume_location = location.width_mm * location.height_mm * location.depth_mm
                    utilization = volume_item / volume_location if volume_location > 0 else 0
                    
                    if 0.5 <= utilization <= 0.9:
                        score += 12
                        reasons.append("Optimal size fit")
                    elif 0.3 <= utilization < 0.5:
                        score += 8
                        reasons.append("Good size fit")
                    else:
                        score += 4
                        reasons.append("Fits (large location)")
                else:
                    score -= 20  # Doesn't fit at all
                    reasons.append("⚠️ Item may not fit")
            
            # Score 5: Tag matching - similar items based on tags
            if item_tags:
                tag_matches = 0
                for item_loc in location.item_locations:
                    item_tags_list = item_loc.item.tags.split(',') if item_loc.item.tags else []
                    item_tags_list = [t.strip() for t in item_tags_list]
                    
                    # Check for tag overlap
                    common_tags = set(item_tags) & set(item_tags_list)
                    if common_tags:
                        tag_matches += len(common_tags)
                
                if tag_matches > 0:
                    score += tag_matches * 5
                    reasons.append(f"Similar tagged items ({tag_matches} matching tags)")
            
            # Score 6: Module-based organization bonus
            # Prefer grouping by general purpose (e.g., all fasteners in one module)
            if item_category:
                module_category_count = 0
                for loc in location.level.locations if location.level else []:
                    for item_loc in loc.item_locations:
                        if item_loc.item.category == item_category:
                            module_category_count += 1
                
                if module_category_count > 5:
                    score += 10
                    reasons.append(f"Module specializes in {item_category}")
            
            # Only include locations with positive scores
            if score > 0:
                suggestions.append(LocationSuggestion(location, score, reasons))
        
        # Sort by score (highest first) and return top N
        suggestions.sort(key=lambda x: x.score, reverse=True)
        return suggestions[:limit]
    
    @staticmethod
    def suggest_for_item(item: Item, limit: int = 5) -> List[LocationSuggestion]:
        """
        Generate location suggestions for an existing item
        
        Args:
            item: Item object to suggest locations for
            limit: Maximum number of suggestions
        
        Returns:
            List of LocationSuggestion objects
        """
        tags = item.tags.split(',') if item.tags else []
        tags = [t.strip() for t in tags]
        
        # Extract dimensions from metadata if available
        width = None
        height = None
        depth = None
        if item.item_metadata:
            width = item.item_metadata.get('width_mm')
            height = item.item_metadata.get('height_mm')
            depth = item.item_metadata.get('depth_mm')
        
        return LocationSuggestionService.suggest_locations(
            item_category=item.category,
            item_type=item.item_type,
            item_tags=tags,
            width_mm=width,
            height_mm=height,
            depth_mm=depth,
            limit=limit
        )
