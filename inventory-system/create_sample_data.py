#!/usr/bin/env python3
"""
Test script to populate the inventory system with sample data
Run this after the system is deployed to see it in action
"""

import requests
import time

BASE_URL = "http://localhost:8080"

def wait_for_server():
    """Wait for the server to be ready"""
    print("Waiting for server to be ready...")
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(BASE_URL)
            if response.status_code == 200:
                print("✓ Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
    print("✗ Server did not start in time")
    return False

def create_sample_data():
    """Create sample modules, levels, and items"""
    
    print("\n" + "="*60)
    print("Creating Sample Data for Inventory System")
    print("="*60 + "\n")
    
    # Sample modules
    modules = [
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
            "description": "Tools and equipment",
            "location_description": "Tool wall, west side"
        }
    ]
    
    created_modules = []
    
    # Create modules
    print("Creating modules...")
    for module_data in modules:
        try:
            response = requests.post(f"{BASE_URL}/modules/new", data=module_data, allow_redirects=False)
            if response.status_code in [200, 302]:
                print(f"  ✓ Created module: {module_data['name']}")
                created_modules.append(module_data['name'])
            else:
                print(f"  ✗ Failed to create module: {module_data['name']}")
        except Exception as e:
            print(f"  ✗ Error creating module {module_data['name']}: {e}")
    
    # Get module IDs
    try:
        response = requests.get(f"{BASE_URL}/modules/api/modules")
        modules_list = response.json()
        module_map = {m['name']: m['id'] for m in modules_list}
    except:
        print("✗ Failed to get module list")
        return
    
    # Sample levels for each module
    levels_data = {
        "Zeus": [
            {"level_number": 1, "name": "Top Drawer", "rows": 4, "columns": 6, "description": "Small components"},
            {"level_number": 2, "name": "Middle Drawer", "rows": 3, "columns": 4, "description": "Medium bins"},
            {"level_number": 3, "name": "Bottom Drawer", "rows": 2, "columns": 3, "description": "Large storage"}
        ],
        "Muse": [
            {"level_number": 1, "rows": 5, "columns": 8, "description": "Metric fasteners"},
            {"level_number": 2, "rows": 5, "columns": 8, "description": "Imperial fasteners"},
            {"level_number": 3, "rows": 4, "columns": 6, "description": "Specialty hardware"}
        ],
        "Apollo": [
            {"level_number": 1, "rows": 2, "columns": 4, "description": "Hand tools"},
            {"level_number": 2, "rows": 2, "columns": 3, "description": "Power tools"}
        ]
    }
    
    print("\nCreating levels...")
    for module_name, levels in levels_data.items():
        if module_name not in module_map:
            continue
        
        module_id = module_map[module_name]
        for level_data in levels:
            try:
                response = requests.post(f"{BASE_URL}/modules/{module_id}/levels/new", data=level_data, allow_redirects=False)
                if response.status_code in [200, 302]:
                    print(f"  ✓ Created {module_name} Level {level_data['level_number']}")
                else:
                    print(f"  ✗ Failed to create level {level_data['level_number']} in {module_name}")
            except Exception as e:
                print(f"  ✗ Error creating level: {e}")
    
    # Sample items
    items_data = [
        {
            "name": "M6 Hex Bolts",
            "description": "Hex head bolt, M6 diameter, 50mm long, zinc plated, metric thread",
            "category": "Fasteners",
            "item_type": "solid",
            "quantity": 100,
            "unit": "pieces",
            "tags": "bolt, metric, m6, hex, zinc, fastener"
        },
        {
            "name": "1kΩ Resistors",
            "description": "1/4 watt carbon film resistor, 1000 ohm, 5% tolerance, through-hole",
            "category": "Electronics",
            "item_type": "solid",
            "quantity": 200,
            "unit": "pieces",
            "tags": "resistor, 1k, 1000ohm, carbon film, electronics"
        },
        {
            "name": "Arduino Uno R3",
            "description": "Arduino Uno R3 development board, ATmega328P microcontroller, USB interface",
            "category": "Electronics",
            "item_type": "solid",
            "quantity": 5,
            "unit": "pieces",
            "tags": "arduino, uno, microcontroller, development board"
        },
        {
            "name": "#8 Wood Screws",
            "description": "Phillips pan head wood screw, #8 size, 3/4 inch long, zinc plated",
            "category": "Fasteners",
            "item_type": "solid",
            "quantity": 250,
            "unit": "pieces",
            "tags": "screw, wood screw, phillips, pan head, #8"
        },
        {
            "name": "SMD Capacitors 0.1µF",
            "description": "Ceramic capacitor, 0.1 microfarad, 0805 package, 50V rating",
            "category": "Electronics",
            "item_type": "smd_component",
            "quantity": 500,
            "unit": "pieces",
            "tags": "capacitor, smd, 0805, ceramic, 0.1uf"
        },
        {
            "name": "Red Spray Paint",
            "description": "Rust-Oleum 2X Ultra Cover Paint+Primer, gloss red, 12 oz aerosol",
            "category": "Paints & Coatings",
            "item_type": "liquid",
            "quantity": 3,
            "unit": "cans",
            "tags": "paint, spray paint, red, rust-oleum"
        },
        {
            "name": "Phillips Screwdriver",
            "description": "Phillips head screwdriver, #2 size, 6 inch shaft, cushion grip handle",
            "category": "Tools",
            "item_type": "tool",
            "quantity": 2,
            "unit": "pieces",
            "tags": "screwdriver, phillips, hand tool"
        },
        {
            "name": "M3 Standoffs",
            "description": "Aluminum standoff, M3 thread, 10mm length, hex body",
            "category": "Hardware",
            "item_type": "solid",
            "quantity": 50,
            "unit": "pieces",
            "tags": "standoff, m3, metric, aluminum, spacer"
        },
        {
            "name": "LED 5mm Red",
            "description": "Light emitting diode, 5mm diameter, red, 2V forward voltage, 20mA",
            "category": "Electronics",
            "item_type": "solid",
            "quantity": 100,
            "unit": "pieces",
            "tags": "led, red, 5mm, light, electronics"
        },
        {
            "name": "Zip Ties 6 inch",
            "description": "Nylon cable tie, 6 inch length, 40 lb tensile strength, black",
            "category": "Hardware",
            "item_type": "bulk",
            "quantity": 500,
            "unit": "pieces",
            "tags": "zip tie, cable tie, nylon, fastener"
        }
    ]
    
    print("\nCreating items...")
    for item_data in items_data:
        try:
            response = requests.post(f"{BASE_URL}/items/new", data=item_data, allow_redirects=False)
            if response.status_code in [200, 302]:
                print(f"  ✓ Created item: {item_data['name']}")
            else:
                print(f"  ✗ Failed to create item: {item_data['name']}")
        except Exception as e:
            print(f"  ✗ Error creating item {item_data['name']}: {e}")
    
    print("\n" + "="*60)
    print("Sample data creation complete!")
    print("="*60)
    print(f"\nYou can now access the system at: {BASE_URL}")
    print("\nTry these features:")
    print("  • Browse Modules to see the storage hierarchy")
    print("  • View Items to see the inventory")
    print("  • Use Search to find items by keyword")
    print("  • Click on levels to see the location grid")
    print("\n")

if __name__ == "__main__":
    print("\n🏠 Homelab Inventory System - Sample Data Generator\n")
    
    if wait_for_server():
        time.sleep(2)  # Give it a moment to fully initialize
        create_sample_data()
    else:
        print("\nMake sure the system is running:")
        print("  docker-compose up -d")
        print("\nThen run this script again.")
