"""
Specification Parser Service for Phase 3: Duplicate Detection

This service extracts structured information from natural language item descriptions.
It recognizes common patterns for:
- Fasteners (M6, #8, 1/4 inch screws, etc.)
- Electronics (resistors, capacitors, IC packages)
- Tools and measurements
- Dimensions and sizes

The extracted specifications are used for:
1. Duplicate detection (comparing items)
2. Auto-populating metadata and tags
3. Standardizing units and formats
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedSpec:
    """Container for parsed specifications"""
    category: Optional[str] = None
    specs: Dict[str, any] = None
    tags: List[str] = None
    confidence: float = 0.0  # 0.0 to 1.0
    
    def __post_init__(self):
        if self.specs is None:
            self.specs = {}
        if self.tags is None:
            self.tags = []


class SpecificationParser:
    """Parse item descriptions to extract structured specifications"""
    
    # Fastener patterns
    METRIC_FASTENER = re.compile(
        r'M(\d+)(?:\s*[xX×]\s*(\d+(?:\.\d+)?))?',  # M6x50 or M6
        re.IGNORECASE
    )
    
    IMPERIAL_FASTENER_NUM = re.compile(
        r'#(\d+)(?:\s*[xX×]\s*([0-9/]+))?',  # #8 x 3/4
        re.IGNORECASE
    )
    
    FRACTION_INCH = re.compile(
        r'(\d+/\d+)\s*(?:inch|in|")',  # 3/4 inch, 1/2", etc.
        re.IGNORECASE
    )
    
    DECIMAL_INCH = re.compile(
        r'(\d+\.?\d*)\s*(?:inch|in|")',  # 0.75 inch
        re.IGNORECASE
    )
    
    # Electronics patterns
    RESISTOR = re.compile(
        r'(\d+\.?\d*)\s*([kMGmμu]?)(?:ohm|Ω|R)',  # 1kΩ, 10Ω, 4.7k
        re.IGNORECASE
    )
    
    CAPACITOR = re.compile(
        r'(\d+\.?\d*)\s*([μunp]?)F',  # 0.1μF, 100nF, 10pF
        re.IGNORECASE
    )
    
    IC_PACKAGE = re.compile(
        r'\b(0201|0402|0603|0805|1206|1210|SOT-?23|SOT-?89|SOIC|TSSOP|QFN|DIP-?\d+)\b',
        re.IGNORECASE
    )
    
    # Measurement patterns
    METRIC_LENGTH = re.compile(
        r'(\d+\.?\d*)\s*(mm|cm|m)(?:\s|$)',  # 10mm, 5.5cm
        re.IGNORECASE
    )
    
    METRIC_WEIGHT = re.compile(
        r'(\d+\.?\d*)\s*(g|kg)(?:\s|$)',  # 100g, 1.5kg
        re.IGNORECASE
    )
    
    # Dimensions pattern (LxWxH)
    DIMENSIONS = re.compile(
        r'(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)(?:\s*[xX×]\s*(\d+\.?\d*))?(?:\s*(mm|cm|in))?',
        re.IGNORECASE
    )
    
    # Head types for fasteners
    HEAD_TYPES = [
        'pan head', 'flat head', 'round head', 'hex head', 'button head',
        'socket head', 'cap head', 'countersunk', 'Phillips', 'flathead',
        'hex bolt', 'carriage bolt', 'machine screw'
    ]
    
    # Material keywords
    MATERIALS = [
        'steel', 'stainless', 'brass', 'aluminum', 'plastic', 'nylon',
        'titanium', 'copper', 'zinc', 'galvanized', 'chrome'
    ]
    
    def parse(self, description: str, name: str = "") -> ParsedSpec:
        """
        Main entry point: parse description and return structured specs
        
        Args:
            description: Natural language description
            name: Item name (optional, checked too)
            
        Returns:
            ParsedSpec with category, specs, tags, and confidence
        """
        full_text = f"{name} {description}".strip()
        
        # Try parsers in order of specificity
        parsers = [
            self.parse_fastener,
            self.parse_resistor,
            self.parse_capacitor,
            self.parse_ic_package,
            self.parse_dimensions
        ]
        
        best_result = ParsedSpec()
        
        for parser in parsers:
            result = parser(full_text)
            if result.confidence > best_result.confidence:
                best_result = result
        
        # Add general measurements if not already categorized
        if best_result.confidence < 0.5:
            measurements = self.extract_measurements(full_text)
            if measurements:
                best_result.specs.update(measurements)
                best_result.tags.extend(self._make_tags(measurements))
        
        # Add material tags
        materials = self.extract_materials(full_text)
        if materials:
            best_result.tags.extend(materials)
        
        return best_result
    
    def parse_fastener(self, text: str) -> ParsedSpec:
        """Parse fastener specifications (screws, bolts, nuts)"""
        result = ParsedSpec(category="fastener")
        
        # Check for metric fasteners (M6, M8x50, etc.)
        metric_match = self.METRIC_FASTENER.search(text)
        if metric_match:
            diameter = int(metric_match.group(1))
            length = metric_match.group(2)
            
            result.specs['thread_size'] = f"M{diameter}"
            result.specs['diameter_mm'] = diameter
            result.tags.append(f"M{diameter}")
            result.confidence = 0.8
            
            if length:
                result.specs['length_mm'] = float(length)
                result.tags.append(f"{length}mm")
                result.confidence = 0.9
        
        # Check for imperial numbered fasteners (#8, #10, etc.)
        imperial_match = self.IMPERIAL_FASTENER_NUM.search(text)
        if imperial_match:
            size_num = int(imperial_match.group(1))
            length = imperial_match.group(2)
            
            result.specs['thread_size'] = f"#{size_num}"
            result.tags.append(f"#{size_num}")
            result.confidence = 0.8
            
            if length:
                result.specs['length_str'] = length
                result.tags.append(f"{length}in")
                result.confidence = 0.9
        
        # Check for fractional inch sizes
        fraction_match = self.FRACTION_INCH.search(text)
        if fraction_match:
            fraction = fraction_match.group(1)
            result.specs['size_fraction'] = fraction
            result.tags.append(f"{fraction}in")
            if result.confidence < 0.7:
                result.confidence = 0.7
        
        # Detect head type
        text_lower = text.lower()
        for head_type in self.HEAD_TYPES:
            if head_type.lower() in text_lower:
                result.specs['head_type'] = head_type
                result.tags.append(head_type.replace(' ', '-'))
                result.confidence = min(1.0, result.confidence + 0.1)
                break
        
        # Detect drive type
        if 'phillips' in text_lower:
            result.specs['drive'] = 'phillips'
            result.tags.append('phillips')
        elif 'flathead' in text_lower or 'slotted' in text_lower:
            result.specs['drive'] = 'flathead'
            result.tags.append('flathead')
        elif 'hex' in text_lower or 'allen' in text_lower:
            result.specs['drive'] = 'hex'
            result.tags.append('hex-drive')
        elif 'torx' in text_lower:
            result.specs['drive'] = 'torx'
            result.tags.append('torx')
        
        return result if result.confidence > 0 else ParsedSpec()
    
    def parse_resistor(self, text: str) -> ParsedSpec:
        """Parse resistor specifications"""
        result = ParsedSpec(category="resistor")
        
        match = self.RESISTOR.search(text)
        if not match:
            return ParsedSpec()
        
        value = float(match.group(1))
        multiplier = match.group(2).lower() if match.group(2) else ''
        
        # Convert to ohms
        multipliers = {
            'k': 1000,
            'm': 1_000_000,
            'g': 1_000_000_000,
            'milli': 0.001,
            'μ': 0.000001,
            'u': 0.000001
        }
        
        ohms = value * multipliers.get(multiplier, 1)
        
        result.specs['resistance_ohms'] = ohms
        result.specs['resistance_str'] = f"{value}{multiplier}Ω"
        result.tags.append(f"{value}{multiplier}Ω")
        result.tags.append('resistor')
        result.confidence = 0.9
        
        # Detect tolerance
        if '1%' in text:
            result.specs['tolerance'] = '1%'
            result.tags.append('1%-tolerance')
        elif '5%' in text:
            result.specs['tolerance'] = '5%'
            result.tags.append('5%-tolerance')
        
        # Detect wattage
        wattage_match = re.search(r'(1/4|1/2|1|2|5)\s*W', text, re.IGNORECASE)
        if wattage_match:
            result.specs['wattage'] = wattage_match.group(1) + 'W'
            result.tags.append(wattage_match.group(1) + 'W')
        
        return result
    
    def parse_capacitor(self, text: str) -> ParsedSpec:
        """Parse capacitor specifications"""
        result = ParsedSpec(category="capacitor")
        
        match = self.CAPACITOR.search(text)
        if not match:
            return ParsedSpec()
        
        value = float(match.group(1))
        multiplier = match.group(2).lower() if match.group(2) else ''
        
        # Convert to farads
        multipliers = {
            'μ': 1e-6,
            'u': 1e-6,
            'n': 1e-9,
            'p': 1e-12
        }
        
        farads = value * multipliers.get(multiplier, 1)
        
        result.specs['capacitance_farads'] = farads
        result.specs['capacitance_str'] = f"{value}{multiplier}F"
        result.tags.append(f"{value}{multiplier}F")
        result.tags.append('capacitor')
        result.confidence = 0.9
        
        # Detect voltage rating
        voltage_match = re.search(r'(\d+)\s*V', text, re.IGNORECASE)
        if voltage_match:
            result.specs['voltage'] = int(voltage_match.group(1))
            result.tags.append(f"{voltage_match.group(1)}V")
        
        # Detect type
        text_lower = text.lower()
        if 'ceramic' in text_lower:
            result.specs['type'] = 'ceramic'
            result.tags.append('ceramic')
        elif 'electrolytic' in text_lower:
            result.specs['type'] = 'electrolytic'
            result.tags.append('electrolytic')
        elif 'tantalum' in text_lower:
            result.specs['type'] = 'tantalum'
            result.tags.append('tantalum')
        
        return result
    
    def parse_ic_package(self, text: str) -> ParsedSpec:
        """Parse IC package specifications (SMD sizes, package types)"""
        result = ParsedSpec(category="electronics")
        
        match = self.IC_PACKAGE.search(text)
        if not match:
            return ParsedSpec()
        
        package = match.group(1).upper()
        result.specs['package'] = package
        result.tags.append(package.lower())
        result.tags.append('smd')
        result.confidence = 0.8
        
        return result
    
    def parse_dimensions(self, text: str) -> ParsedSpec:
        """Parse physical dimensions (LxWxH)"""
        result = ParsedSpec()
        
        match = self.DIMENSIONS.search(text)
        if not match:
            return ParsedSpec()
        
        length = float(match.group(1))
        width = float(match.group(2))
        height = float(match.group(3)) if match.group(3) else None
        unit = match.group(4).lower() if match.group(4) else 'mm'
        
        result.specs['length'] = length
        result.specs['width'] = width
        if height:
            result.specs['height'] = height
            result.tags.append(f"{length}x{width}x{height}{unit}")
        else:
            result.tags.append(f"{length}x{width}{unit}")
        
        result.specs['unit'] = unit
        result.confidence = 0.6
        
        return result
    
    def extract_measurements(self, text: str) -> Dict[str, any]:
        """Extract general measurements (length, weight)"""
        measurements = {}
        
        # Metric lengths
        length_match = self.METRIC_LENGTH.search(text)
        if length_match:
            value = float(length_match.group(1))
            unit = length_match.group(2).lower()
            measurements[f'length_{unit}'] = value
        
        # Metric weights
        weight_match = self.METRIC_WEIGHT.search(text)
        if weight_match:
            value = float(weight_match.group(1))
            unit = weight_match.group(2).lower()
            measurements[f'weight_{unit}'] = value
        
        return measurements
    
    def extract_materials(self, text: str) -> List[str]:
        """Extract material keywords"""
        text_lower = text.lower()
        found_materials = []
        
        for material in self.MATERIALS:
            if material.lower() in text_lower:
                found_materials.append(material)
        
        return found_materials
    
    def _make_tags(self, specs: Dict) -> List[str]:
        """Convert specs dict to tag strings"""
        tags = []
        for key, value in specs.items():
            if isinstance(value, (int, float)):
                tags.append(f"{key}:{value}")
        return tags
    
    @staticmethod
    def standardize_unit(value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert between units"""
        conversions = {
            # Length
            ('mm', 'in'): 0.0393701,
            ('cm', 'in'): 0.393701,
            ('in', 'mm'): 25.4,
            ('in', 'cm'): 2.54,
            # Weight
            ('g', 'oz'): 0.035274,
            ('kg', 'lb'): 2.20462,
            ('oz', 'g'): 28.3495,
            ('lb', 'kg'): 0.453592,
        }
        
        key = (from_unit.lower(), to_unit.lower())
        if key in conversions:
            return value * conversions[key]
        
        return None
