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
    
    # Additional electronics patterns
    RESISTOR = re.compile(
        r'(\d+\.?\d*)\s*([kKmMgG]?)(?:Ω|ohm|ohms)',  # 10kΩ, 1.5MΩ
        re.IGNORECASE
    )
    
    CAPACITOR = re.compile(
        r'(\d+\.?\d*)\s*([μunp]?)(?:F|farad)',  # 10μF, 100nF
        re.IGNORECASE
    )
    
    IC_PACKAGE = re.compile(
        r'\b(0805|0603|0402|1206|1210|SOT-23|SOT-89|TO-220|TO-92|DIP-8|DIP-14|DIP-16|QFN|QFP|BGA)\b',
        re.IGNORECASE
    )
    
    INDUCTOR = re.compile(
        r'(\d+\.?\d*)\s*([μumH]?)(?:H|henry)',  # 10μH, 1mH
        re.IGNORECASE
    )
    
    DIODE_PACKAGE = re.compile(
        r'\b(DO-?214|DO-?41|SOD-?123|SOD-?323|TO-?220|TO-?92)\b',
        re.IGNORECASE
    )
    
    TRANSISTOR_PACKAGE = re.compile(
        r'\b(TO-?18|TO-?39|TO-?92|TO-?220|TO-?247|SOT-?23|SOT-?89)\b',
        re.IGNORECASE
    )
    
    # Chemical patterns
    CHEMICAL_FORMULA = re.compile(
        r'\b([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*)\b',  # H2O, NaCl, C6H12O6
    )
    
    CONCENTRATION = re.compile(
        r'(\d+(?:\.\d+)?)\s*(%|M|mol/L|molar|N|normal)',  # 10%, 0.1M, 5N
        re.IGNORECASE
    )
    
    # Tool patterns
    DRILL_SIZE = re.compile(
        r'(\d+(?:/\d+)?)\s*(?:inch|in|")\s*drill',  # 1/4" drill
        re.IGNORECASE
    )
    
    WRENCH_SIZE = re.compile(
        r'(\d+(?:/\d+)?)\s*(?:inch|in|")\s*wrench',  # 1/2" wrench
        re.IGNORECASE
    )
    
    # Power supply patterns
    VOLTAGE_CURRENT = re.compile(
        r'(\d+(?:\.\d+)?)\s*V\s*(?:/\s*)?(\d+(?:\.\d+)?)\s*A',  # 12V/2A
        re.IGNORECASE
    )
    
    # Cable/wire patterns
    WIRE_GAUGE = re.compile(
        r'(\d+)\s*(?:AWG|gauge)',  # 18 AWG, 22 gauge
        re.IGNORECASE
    )
    
    WIRE_SIZE = re.compile(
        r'(\d+(?:/\d+)?)\s*(?:mm²|mm2)',  # 2.5mm²
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
    
    # Material keywords (expanded)
    MATERIALS = [
        'steel', 'stainless', 'brass', 'aluminum', 'plastic', 'nylon',
        'titanium', 'copper', 'zinc', 'galvanized', 'chrome', 'bronze',
        'cast iron', 'mild steel', 'carbon steel', 'alloy steel', 'tool steel',
        'silicon', 'germanium', 'gallium', 'arsenic', 'phosphorus',
        'epoxy', 'phenolic', 'fiberglass', 'ceramic', 'porcelain',
        'rubber', 'neoprene', 'silicone', 'teflon', 'kevlar',
        'wood', 'oak', 'pine', 'maple', 'birch', 'cherry', 'walnut'
    ]
    
    # Finish/coating keywords
    FINISHES = [
        'zinc plated', 'galvanized', 'chrome plated', 'nickel plated',
        'anodized', 'powder coated', 'painted', 'enameled', 'lacquered',
        'oiled', 'waxed', 'varnished', 'stained'
    ]
    
    # Color keywords
    COLORS = [
        'red', 'blue', 'green', 'yellow', 'black', 'white', 'gray', 'grey',
        'brown', 'orange', 'purple', 'pink', 'silver', 'gold', 'bronze',
        'copper', 'brass', 'clear', 'transparent', 'opaque'
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
            self.parse_inductor,
            self.parse_diode,
            self.parse_transistor,
            self.parse_ic_package,
            self.parse_power_supply,
            self.parse_wire_cable,
            self.parse_tool,
            self.parse_chemical,
            self.parse_dimensions
        ]
        
        best_result = ParsedSpec()
        
        for parser in parsers:
            result = parser(full_text)
            if result.confidence > best_result.confidence:
                best_result = result
        
        # Recalculate confidence with additional factors
        best_result.confidence = self._calculate_confidence(best_result, full_text)
        
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
        
        # Standardize units where possible
        best_result = self._standardize_units(best_result)
        
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
        
        try:
            match = self.RESISTOR.search(text)
            if not match:
                return ParsedSpec()
            
            value_str = match.group(1)
            multiplier = match.group(2).lower() if match.group(2) else ''
            
            # Handle potential float conversion errors
            try:
                value = float(value_str)
            except ValueError:
                return ParsedSpec()
            
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
            
        except Exception:
            # Return empty result on any parsing error
            return ParsedSpec()
        
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
    
    def parse_inductor(self, text: str) -> ParsedSpec:
        """Parse inductor specifications"""
        result = ParsedSpec(category="inductor")
        
        match = self.INDUCTOR.search(text)
        if not match:
            return ParsedSpec()
        
        value = float(match.group(1))
        multiplier = match.group(2).lower() if match.group(2) else ''
        
        # Convert to henries
        multipliers = {
            'm': 1e-3,
            'μ': 1e-6,
            'u': 1e-6,
            'n': 1e-9,
            'p': 1e-12
        }
        
        henries = value * multipliers.get(multiplier, 1)
        
        result.specs['inductance_henries'] = henries
        result.specs['inductance_str'] = f"{value}{multiplier}H"
        result.tags.append(f"{value}{multiplier}H")
        result.tags.append('inductor')
        result.confidence = 0.9
        
        # Detect current rating
        current_match = re.search(r'(\d+(?:\.\d+)?)\s*A', text, re.IGNORECASE)
        if current_match:
            result.specs['current_rating'] = float(current_match.group(1))
            result.tags.append(f"{current_match.group(1)}A")
        
        return result
    
    def parse_diode(self, text: str) -> ParsedSpec:
        """Parse diode specifications"""
        result = ParsedSpec(category="diode")
        
        # Check for package type
        package_match = self.DIODE_PACKAGE.search(text)
        if package_match:
            result.specs['package'] = package_match.group(1).upper()
            result.tags.append(package_match.group(1).lower())
            result.confidence = 0.7
        
        # Detect diode type
        text_lower = text.lower()
        if 'zener' in text_lower:
            result.specs['type'] = 'zener'
            result.tags.append('zener')
            result.confidence = 0.8
        elif 'schottky' in text_lower:
            result.specs['type'] = 'schottky'
            result.tags.append('schottky')
            result.confidence = 0.8
        elif 'rectifier' in text_lower:
            result.specs['type'] = 'rectifier'
            result.tags.append('rectifier')
            result.confidence = 0.8
        else:
            result.specs['type'] = 'standard'
            result.tags.append('diode')
            result.confidence = 0.6
        
        # Detect voltage rating
        voltage_match = re.search(r'(\d+(?:\.\d+)?)\s*V', text, re.IGNORECASE)
        if voltage_match:
            result.specs['voltage'] = float(voltage_match.group(1))
            result.tags.append(f"{voltage_match.group(1)}V")
        
        # Detect current rating
        current_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:A|mA)', text, re.IGNORECASE)
        if current_match:
            current = float(current_match.group(1))
            unit = 'mA' if 'mA' in text else 'A'
            result.specs['current'] = current
            result.specs['current_unit'] = unit
            result.tags.append(f"{current}{unit}")
        
        return result
    
    def parse_transistor(self, text: str) -> ParsedSpec:
        """Parse transistor specifications"""
        result = ParsedSpec(category="transistor")
        
        # Check for package type
        package_match = self.TRANSISTOR_PACKAGE.search(text)
        if package_match:
            result.specs['package'] = package_match.group(1).upper()
            result.tags.append(package_match.group(1).lower())
            result.confidence = 0.7
        
        # Detect transistor type
        text_lower = text.lower()
        if 'mosfet' in text_lower or 'fet' in text_lower:
            result.specs['type'] = 'MOSFET'
            result.tags.append('mosfet')
            result.confidence = 0.8
        elif 'bjt' in text_lower or 'bipolar' in text_lower:
            result.specs['type'] = 'BJT'
            result.tags.append('bjt')
            result.confidence = 0.8
        else:
            result.specs['type'] = 'transistor'
            result.tags.append('transistor')
            result.confidence = 0.6
        
        # Detect voltage rating
        voltage_match = re.search(r'(\d+(?:\.\d+)?)\s*V', text, re.IGNORECASE)
        if voltage_match:
            result.specs['voltage'] = float(voltage_match.group(1))
            result.tags.append(f"{voltage_match.group(1)}V")
        
        return result
    
    def parse_power_supply(self, text: str) -> ParsedSpec:
        """Parse power supply specifications"""
        result = ParsedSpec(category="power supply")
        
        match = self.VOLTAGE_CURRENT.search(text)
        if match:
            voltage = float(match.group(1))
            current = float(match.group(2))
            
            result.specs['voltage'] = voltage
            result.specs['current'] = current
            result.specs['power'] = voltage * current
            result.tags.append(f"{voltage}V")
            result.tags.append(f"{current}A")
            result.tags.append(f"{voltage*current:.1f}W")
            result.confidence = 0.9
        
        return result
    
    def parse_wire_cable(self, text: str) -> ParsedSpec:
        """Parse wire and cable specifications"""
        result = ParsedSpec(category="wire/cable")
        
        # Check for AWG gauge
        awg_match = self.WIRE_GAUGE.search(text)
        if awg_match:
            gauge = int(awg_match.group(1))
            result.specs['gauge_awg'] = gauge
            result.tags.append(f"{gauge}AWG")
            result.confidence = 0.8
        
        # Check for metric wire size
        size_match = self.WIRE_SIZE.search(text)
        if size_match:
            size = float(size_match.group(1))
            result.specs['cross_section_mm2'] = size
            result.tags.append(f"{size}mm²")
            result.confidence = 0.8
        
        # Detect conductor type
        text_lower = text.lower()
        if 'solid' in text_lower:
            result.specs['conductor_type'] = 'solid'
            result.tags.append('solid-core')
        elif 'stranded' in text_lower:
            result.specs['conductor_type'] = 'stranded'
            result.tags.append('stranded')
        
        # Detect insulation
        if 'teflon' in text_lower or 'ptfe' in text_lower:
            result.specs['insulation'] = 'PTFE'
            result.tags.append('ptfe')
        elif 'pvc' in text_lower:
            result.specs['insulation'] = 'PVC'
            result.tags.append('pvc')
        elif 'silicone' in text_lower:
            result.specs['insulation'] = 'silicone'
            result.tags.append('silicone')
        
        return result
    
    def parse_tool(self, text: str) -> ParsedSpec:
        """Parse tool specifications"""
        result = ParsedSpec(category="tool")
        
        # Check for drill sizes
        drill_match = self.DRILL_SIZE.search(text)
        if drill_match:
            size = drill_match.group(1)
            result.specs['drill_size'] = size
            result.tags.append(f"{size}-drill")
            result.confidence = 0.8
        
        # Check for wrench sizes
        wrench_match = self.WRENCH_SIZE.search(text)
        if wrench_match:
            size = wrench_match.group(1)
            result.specs['wrench_size'] = size
            result.tags.append(f"{size}-wrench")
            result.confidence = 0.8
        
        return result
    
    def parse_chemical(self, text: str) -> ParsedSpec:
        """Parse chemical specifications"""
        result = ParsedSpec(category="chemical")
        
        # Check for chemical formulas
        formula_match = self.CHEMICAL_FORMULA.search(text)
        if formula_match:
            formula = formula_match.group(1)
            result.specs['formula'] = formula
            result.tags.append(formula)
            result.confidence = 0.7
        
        # Check for concentrations
        conc_match = self.CONCENTRATION.search(text)
        if conc_match:
            value = float(conc_match.group(1))
            unit = conc_match.group(2)
            result.specs['concentration'] = value
            result.specs['concentration_unit'] = unit
            result.tags.append(f"{value}{unit}")
            result.confidence = 0.8
        
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
    
    def _calculate_confidence(self, result: ParsedSpec, text: str) -> float:
        """Calculate confidence score based on multiple factors"""
        if not result.category:
            return 0.0
        
        confidence = result.confidence
        
        # Boost confidence if category keywords are present
        category_keywords = {
            'fastener': ['screw', 'bolt', 'nut', 'washer', 'thread'],
            'resistor': ['resistor', 'resistance', 'ohm'],
            'capacitor': ['capacitor', 'capacitance', 'farad'],
            'inductor': ['inductor', 'coil', 'henry'],
            'diode': ['diode', 'rectifier', 'zener', 'schottky'],
            'transistor': ['transistor', 'mosfet', 'fet', 'bjt'],
            'power supply': ['power', 'supply', 'voltage', 'current', 'watt'],
            'wire/cable': ['wire', 'cable', 'gauge', 'awg', 'conductor'],
            'tool': ['drill', 'wrench', 'screwdriver', 'plier'],
            'chemical': ['acid', 'solution', 'concentration', 'formula']
        }
        
        text_lower = text.lower()
        if result.category in category_keywords:
            for keyword in category_keywords[result.category]:
                if keyword in text_lower:
                    confidence = min(1.0, confidence + 0.1)
                    break
        
        # Boost confidence based on number of specs extracted
        spec_count = len(result.specs)
        if spec_count > 3:
            confidence = min(1.0, confidence + 0.1)
        elif spec_count > 1:
            confidence = min(1.0, confidence + 0.05)
        
        return confidence
    
    def _standardize_units(self, result: ParsedSpec) -> ParsedSpec:
        """Standardize units in the parsed result for consistency"""
        if not result.specs:
            return result
        
        # Standardize length units to mm
        for key in ['length_mm', 'length_cm', 'length_in']:
            if key in result.specs:
                value = result.specs[key]
                if key == 'length_cm':
                    result.specs['length_mm'] = value * 10
                elif key == 'length_in':
                    result.specs['length_mm'] = value * 25.4
                # Keep the original unit info
                result.specs[f'{key}_original'] = value
                break
        
        # Standardize weight units to grams
        for key in ['weight_g', 'weight_kg', 'weight_oz', 'weight_lb']:
            if key in result.specs:
                value = result.specs[key]
                if key == 'weight_kg':
                    result.specs['weight_g'] = value * 1000
                elif key == 'weight_oz':
                    result.specs['weight_g'] = value * 28.3495
                elif key == 'weight_lb':
                    result.specs['weight_g'] = value * 453.592
                # Keep the original unit info
                result.specs[f'{key}_original'] = value
                break
        
        return result
    
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
