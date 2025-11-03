#!/usr/bin/env python3
"""
Generate realistic sample data for WhereTF? inventory system
Uses real-world specifications from industry standards
"""

import requests
import time
import random
from typing import List, Dict, Tuple

BASE_URL = "http://localhost:8080"

# ============================================================================
# REAL-WORLD SPECIFICATIONS (from web research)
# ============================================================================

# Metric screw/bolt specifications (ISO 262)
METRIC_SIZES = {
    'M2': {'pitch': 0.4, 'lengths': [4, 6, 8, 10, 12, 16, 20]},
    'M3': {'pitch': 0.5, 'lengths': [6, 8, 10, 12, 16, 20, 25, 30]},
    'M4': {'pitch': 0.7, 'lengths': [8, 10, 12, 16, 20, 25, 30, 35, 40]},
    'M5': {'pitch': 0.8, 'lengths': [10, 12, 16, 20, 25, 30, 35, 40, 50]},
    'M6': {'pitch': 1.0, 'lengths': [12, 16, 20, 25, 30, 35, 40, 50, 60]},
    'M8': {'pitch': 1.25, 'lengths': [16, 20, 25, 30, 35, 40, 50, 60, 70, 80]},
    'M10': {'pitch': 1.5, 'lengths': [20, 25, 30, 35, 40, 50, 60, 70, 80, 100]},
}

# UNC/UNF thread specifications
UNC_SIZES = {
    '#2': {'major_dia': 0.086, 'tpi': 56, 'lengths': [1/4, 3/8, 1/2, 5/8, 3/4]},
    '#4': {'major_dia': 0.112, 'tpi': 40, 'lengths': [1/4, 3/8, 1/2, 5/8, 3/4, 1]},
    '#6': {'major_dia': 0.138, 'tpi': 32, 'lengths': [1/4, 3/8, 1/2, 5/8, 3/4, 1, 1.25]},
    '#8': {'major_dia': 0.164, 'tpi': 32, 'lengths': [3/8, 1/2, 5/8, 3/4, 1, 1.25, 1.5]},
    '#10': {'major_dia': 0.190, 'tpi': 24, 'lengths': [1/2, 5/8, 3/4, 1, 1.25, 1.5, 2]},
    '1/4"': {'major_dia': 0.250, 'tpi': 20, 'lengths': [1/2, 5/8, 3/4, 1, 1.25, 1.5, 2, 2.5, 3]},
    '5/16"': {'major_dia': 0.3125, 'tpi': 18, 'lengths': [3/4, 1, 1.25, 1.5, 2, 2.5, 3]},
    '3/8"': {'major_dia': 0.375, 'tpi': 16, 'lengths': [1, 1.25, 1.5, 2, 2.5, 3, 3.5, 4]},
}

# Screw head styles
HEAD_STYLES = [
    'hex head', 'socket head cap', 'button head', 'pan head',
    'flat head', 'oval head', 'round head', 'truss head'
]

# Drive types
DRIVE_TYPES = ['hex socket', 'Phillips', 'Torx', 'slotted', 'hex', 'Pozidriv']

# Fastener materials and finishes
MATERIALS = [
    'steel zinc plated', 'stainless steel A2', 'stainless steel A4',
    'steel black oxide', 'brass', 'nylon', 'steel hot-dip galvanized'
]

# Resistor E12 series (±10% tolerance) - base values per decade
E12_RESISTOR_VALUES = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

# Resistor multipliers (decades from 1Ω to 10MΩ)
RESISTOR_DECADES = [
    ('', 1),           # 1Ω - 8.2Ω
    ('0', 10),         # 10Ω - 82Ω
    ('00', 100),       # 100Ω - 820Ω
    ('k', 1000),       # 1kΩ - 8.2kΩ
    ('0k', 10000),     # 10kΩ - 82kΩ
    ('00k', 100000),   # 100kΩ - 820kΩ
    ('M', 1000000),    # 1MΩ - 8.2MΩ
    ('0M', 10000000),  # 10MΩ
]

# Capacitor E6 series (±20% tolerance) - base values per decade
E6_CAPACITOR_VALUES = [1.0, 1.5, 2.2, 3.3, 4.7, 6.8]

# Capacitor decades (from 1pF to 1000µF)
CAPACITOR_DECADES = [
    ('pF', 1e-12),
    ('0pF', 10e-12),
    ('00pF', 100e-12),
    ('nF', 1e-9),
    ('0nF', 10e-9),
    ('00nF', 100e-9),
    ('µF', 1e-6),
    ('0µF', 10e-6),
    ('00µF', 100e-6),
    ('000µF', 1000e-6),
]

# SMD package sizes (metric code)
SMD_PACKAGES = {
    '0402': {'mm': (1.0, 0.5), 'inch': (0.04, 0.02)},
    '0603': {'mm': (1.5, 0.8), 'inch': (0.06, 0.03)},
    '0805': {'mm': (2.0, 1.3), 'inch': (0.08, 0.05)},
    '1206': {'mm': (3.0, 1.5), 'inch': (0.12, 0.06)},
    '1210': {'mm': (3.2, 2.5), 'inch': (0.125, 0.10)},
    '2010': {'mm': (5.0, 2.5), 'inch': (0.20, 0.10)},
}

# Through-hole component types
THROUGH_HOLE_PACKAGES = ['axial', 'radial', 'DIP-8', 'DIP-14', 'DIP-16', 'TO-220', 'TO-92']

# Washer types
WASHER_TYPES = [
    'flat', 'lock', 'split lock', 'wave', 'fender', 'finishing', 'tooth lock'
]

# Washer materials
WASHER_MATERIALS = [
    'steel zinc plated', 'stainless steel', 'brass', 'nylon', 'rubber'
]

# ============================================================================
# DATA GENERATORS
# ============================================================================

def generate_metric_fasteners(count: int = 50) -> List[Dict]:
    """Generate metric screws/bolts with realistic specifications"""
    items = []

    for _ in range(count):
        size = random.choice(list(METRIC_SIZES.keys()))
        spec = METRIC_SIZES[size]
        length = random.choice(spec['lengths'])
        head = random.choice(HEAD_STYLES)
        material = random.choice(MATERIALS)
        drive = random.choice(DRIVE_TYPES) if 'socket' in head or 'pan' in head or 'flat' in head else None

        # Create name and description
        name = f"{size} {head} screw, {length}mm"

        desc_parts = [
            head.capitalize() + ' screw',
            f"{size} thread (pitch {spec['pitch']}mm)",
            f"{length}mm length",
            material
        ]
        if drive:
            desc_parts.insert(1, drive + ' drive')

        description = ', '.join(desc_parts)

        items.append({
            'name': name,
            'description': description,
            'category': 'Fasteners',
            'item_type': 'screw',
            'tags': f"{size},{length}mm,metric,{head.replace(' ', '_')},{material.replace(' ', '_')}",
            'data_source': 'sample_fasteners_metric',
            'raw_input': f"{size} {head} {length}mm {material}"
        })

    return items

def generate_unc_fasteners(count: int = 30) -> List[Dict]:
    """Generate UNC/UNF screws with imperial specifications"""
    items = []

    for _ in range(count):
        size = random.choice(list(UNC_SIZES.keys()))
        spec = UNC_SIZES[size]
        length = random.choice(spec['lengths'])
        head = random.choice(HEAD_STYLES)
        material = random.choice(MATERIALS)

        # Format length as fraction
        if length < 1:
            length_str = f"{int(length * 4)}/4\""
        else:
            whole = int(length)
            frac = length - whole
            if frac == 0:
                length_str = f"{whole}\""
            else:
                length_str = f"{whole}-{int(frac * 4)}/4\""

        name = f"{size}-{spec['tpi']} {head} screw, {length_str}"

        description = f"{head.capitalize()} screw, {size}-{spec['tpi']} UNC thread, {length_str} length, {material}"

        items.append({
            'name': name,
            'description': description,
            'category': 'Fasteners',
            'item_type': 'screw',
            'tags': f"{size},UNC,imperial,{head.replace(' ', '_')},{material.replace(' ', '_')}",
            'data_source': 'sample_fasteners_unc',
            'raw_input': f"{size} {head} {length_str} {material}"
        })

    return items

def generate_resistors(count: int = 40) -> List[Dict]:
    """Generate resistors with E12 standard values"""
    items = []

    for _ in range(count):
        base_value = random.choice(E12_RESISTOR_VALUES)
        decade_suffix, multiplier = random.choice(RESISTOR_DECADES)
        value_ohms = base_value * multiplier

        # Format value with unit
        if multiplier >= 1000000:
            value_str = f"{base_value}MΩ" if multiplier == 1000000 else f"{base_value * 10}MΩ"
        elif multiplier >= 1000:
            if multiplier == 1000:
                value_str = f"{base_value}kΩ"
            elif multiplier == 10000:
                value_str = f"{base_value * 10}kΩ"
            else:
                value_str = f"{base_value * 100}kΩ"
        else:
            value_str = f"{int(base_value * multiplier)}Ω"

        package = random.choice(list(SMD_PACKAGES.keys()) + THROUGH_HOLE_PACKAGES[:2])
        tolerance = '±5%' if random.random() > 0.5 else '±10%'
        power = random.choice(['1/8W', '1/4W', '1/2W', '1W'])

        name = f"{value_str} resistor, {package}"

        desc_parts = [
            f"Resistor {value_str}",
            f"{tolerance} tolerance",
            f"{power} power rating"
        ]

        if package in SMD_PACKAGES:
            desc_parts.append(f"{package} SMD package")
        else:
            desc_parts.append(f"{package} lead")

        description = ', '.join(desc_parts)

        items.append({
            'name': name,
            'description': description,
            'category': 'Electronics',
            'item_type': 'resistor',
            'tags': f"resistor,{value_str},{package},{tolerance}",
            'data_source': 'sample_electronics_resistors',
            'raw_input': f"{value_str} resistor {package}"
        })

    return items

def generate_capacitors(count: int = 40) -> List[Dict]:
    """Generate capacitors with E6 standard values"""
    items = []

    for _ in range(count):
        base_value = random.choice(E6_CAPACITOR_VALUES)
        decade_suffix, multiplier = random.choice(CAPACITOR_DECADES)

        # Format value with unit
        if multiplier >= 1e-6:  # µF range
            if multiplier == 1e-6:
                value_str = f"{base_value}µF"
            elif multiplier == 10e-6:
                value_str = f"{base_value * 10}µF"
            elif multiplier == 100e-6:
                value_str = f"{base_value * 100}µF"
            else:
                value_str = f"{int(base_value * 1000)}µF"
        elif multiplier >= 1e-9:  # nF range
            if multiplier == 1e-9:
                value_str = f"{base_value}nF"
            elif multiplier == 10e-9:
                value_str = f"{base_value * 10}nF"
            else:
                value_str = f"{base_value * 100}nF"
        else:  # pF range
            value_int = int(base_value * (multiplier * 1e12))
            value_str = f"{value_int}pF"

        cap_type = random.choice(['ceramic', 'electrolytic', 'film', 'tantalum'])
        package = random.choice(list(SMD_PACKAGES.keys()) + THROUGH_HOLE_PACKAGES[:2])
        voltage = random.choice(['16V', '25V', '50V', '100V'])

        name = f"{value_str} {cap_type} capacitor, {package}"

        desc_parts = [
            f"{cap_type.capitalize()} capacitor {value_str}",
            f"{voltage} rated voltage"
        ]

        if package in SMD_PACKAGES:
            desc_parts.append(f"{package} SMD package")
        else:
            desc_parts.append(f"{package} lead")

        description = ', '.join(desc_parts)

        items.append({
            'name': name,
            'description': description,
            'category': 'Electronics',
            'item_type': 'capacitor',
            'tags': f"capacitor,{value_str},{cap_type},{package}",
            'data_source': 'sample_electronics_capacitors',
            'raw_input': f"{value_str} {cap_type} capacitor {package}"
        })

    return items

def generate_washers(count: int = 25) -> List[Dict]:
    """Generate washers with realistic specifications"""
    items = []

    # Metric washer sizes for M3-M10
    metric_sizes = ['M3', 'M4', 'M5', 'M6', 'M8', 'M10']

    for _ in range(count):
        washer_type = random.choice(WASHER_TYPES)
        size = random.choice(metric_sizes)
        material = random.choice(WASHER_MATERIALS)

        name = f"{size} {washer_type} washer, {material}"

        description = f"{washer_type.capitalize()} washer for {size} bolts/screws, {material}"

        items.append({
            'name': name,
            'description': description,
            'category': 'Fasteners',
            'item_type': 'washer',
            'tags': f"washer,{size},{washer_type.replace(' ', '_')},{material.replace(' ', '_')}",
            'data_source': 'sample_washers',
            'raw_input': f"{size} {washer_type} washer {material}"
        })

    return items

def create_intentional_duplicates(items: List[Dict]) -> List[Dict]:
    """Create intentional duplicates with slight variations for testing"""
    duplicates = []

    # Pick 10 random items to duplicate
    samples = random.sample(items, min(10, len(items)))

    for item in samples:
        # Create variations
        variations = [
            # Spelling variation
            {**item, 'name': item['name'].replace('screw', 'bolt') if 'screw' in item['name'] else item['name']},
            # Description reorder
            {**item, 'description': ', '.join(reversed(item['description'].split(', ')))},
            # Abbreviation
            {**item, 'name': item['name'].replace('millimeter', 'mm').replace('stainless steel', 'SS')},
        ]

        # Add one random variation
        duplicates.append(random.choice(variations))

    return duplicates

# ============================================================================
# API HELPERS
# ============================================================================

def wait_for_server(max_attempts=30):
    """Wait for server to be ready"""
    print("Waiting for server...")
    for i in range(max_attempts):
        try:
            response = requests.get(BASE_URL)
            if response.status_code == 200:
                print("✓ Server ready!")
                return True
        except:
            pass
        time.sleep(1)
    print("✗ Server not ready")
    return False

def create_sample_modules():
    """Create storage modules"""
    print("\n" + "="*60)
    print("Creating Storage Modules")
    print("="*60)

    modules_data = [
        {
            "name": "Zeus",
            "description": "Main electronics and component storage",
            "location_description": "North wall, workshop"
        },
        {
            "name": "Muse",
            "description": "Fasteners and hardware storage",
            "location_description": "East wall, near workbench"
        },
        {
            "name": "Apollo",
            "description": "Tools and small parts",
            "location_description": "West wall"
        }
    ]

    for mod_data in modules_data:
        # Create module...
        # (implementation continues...)

def main():
    """Generate and upload all sample data"""

    if not wait_for_server():
        return

    print("\n" + "="*60)
    print("WhereTF? - Realistic Sample Data Generator")
    print("Using real-world industry specifications")
    print("="*60)

    # Generate all items
    print("\nGenerating items...")
    all_items = []

    all_items.extend(generate_metric_fasteners(50))
    all_items.extend(generate_unc_fasteners(30))
    all_items.extend(generate_resistors(40))
    all_items.extend(generate_capacitors(40))
    all_items.extend(generate_washers(25))

    # Add intentional duplicates
    duplicates = create_intentional_duplicates(all_items)
    all_items.extend(duplicates)

    print(f"✓ Generated {len(all_items)} items")
    print(f"  - {len([i for i in all_items if i['data_source'] == 'sample_fasteners_metric'])} metric fasteners")
    print(f"  - {len([i for i in all_items if i['data_source'] == 'sample_fasteners_unc'])} UNC fasteners")
    print(f"  - {len([i for i in all_items if i['data_source'] == 'sample_electronics_resistors'])} resistors")
    print(f"  - {len([i for i in all_items if i['data_source'] == 'sample_electronics_capacitors'])} capacitors")
    print(f"  - {len([i for i in all_items if i['data_source'] == 'sample_washers'])} washers")
    print(f"  - {len(duplicates)} intentional duplicates for testing")

    # TODO: Create modules, locations, and upload items
    # This will be completed in the next iteration

    print("\n" + "="*60)
    print("Sample data generation complete!")
    print("="*60)

if __name__ == '__main__':
    main()
