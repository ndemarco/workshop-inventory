"""
Unit tests for SpecificationParser (Phase 3)

Tests the ability to parse various item descriptions and extract structured specs.
"""

import sys
sys.path.insert(0, '/workspaces/wheretf/inventory-system/backend')

from app.services.spec_parser import SpecificationParser


def test_metric_fasteners():
    """Test parsing metric fasteners"""
    parser = SpecificationParser()
    
    # Test M6 screw
    result = parser.parse("M6x50 pan head phillips screw", "")
    assert result.category == "fastener"
    assert result.specs['thread_size'] == "M6"
    assert result.specs['diameter_mm'] == 6
    assert result.specs['length_mm'] == 50.0
    assert result.specs['head_type'] == "pan head"
    assert result.specs['drive'] == "phillips"
    assert "M6" in result.tags
    assert "50mm" in result.tags
    print("✅ M6x50 screw parsed correctly")
    
    # Test M8 bolt
    result = parser.parse("Hex head bolt M8x40 stainless steel", "")
    assert result.category == "fastener"
    assert result.specs['thread_size'] == "M8"
    assert result.specs['diameter_mm'] == 8
    assert result.specs['length_mm'] == 40.0
    assert "stainless" in result.tags
    print("✅ M8x40 bolt parsed correctly")


def test_imperial_fasteners():
    """Test parsing imperial fasteners"""
    parser = SpecificationParser()
    
    # Test #8 screw
    result = parser.parse("#8 x 3/4 flathead screw", "")
    assert result.category == "fastener"
    assert result.specs['thread_size'] == "#8"
    assert result.specs['length_str'] == "3/4"
    assert "#8" in result.tags
    print("✅ #8 x 3/4 screw parsed correctly")
    
    # Test #10 screw
    result = parser.parse("Pan head #10 x 1/2 inch phillips screw", "")
    assert result.category == "fastener"
    assert result.specs['thread_size'] == "#10"
    assert result.specs['head_type'] == "pan head"
    assert result.specs['drive'] == "phillips"
    print("✅ #10 screw parsed correctly")


def test_resistors():
    """Test parsing resistors"""
    parser = SpecificationParser()
    
    # Test 1kΩ resistor
    result = parser.parse("1kΩ resistor 1/4W 5% tolerance", "")
    assert result.category == "resistor"
    assert result.specs['resistance_ohms'] == 1000
    assert result.specs['resistance_str'] == "1kΩ"
    assert result.specs['wattage'] == "1/4W"
    assert result.specs['tolerance'] == "5%"
    assert "1kΩ" in result.tags
    print("✅ 1kΩ resistor parsed correctly")
    
    # Test 10Ω resistor
    result = parser.parse("10 ohm resistor", "")
    assert result.category == "resistor"
    assert result.specs['resistance_ohms'] == 10
    print("✅ 10Ω resistor parsed correctly")
    
    # Test 4.7MΩ resistor
    result = parser.parse("4.7MΩ resistor 1W", "")
    assert result.category == "resistor"
    assert result.specs['resistance_ohms'] == 4_700_000
    assert result.specs['wattage'] == "1W"
    print("✅ 4.7MΩ resistor parsed correctly")


def test_capacitors():
    """Test parsing capacitors"""
    parser = SpecificationParser()
    
    # Test 0.1μF capacitor
    result = parser.parse("0.1μF ceramic capacitor 50V", "")
    assert result.category == "capacitor"
    assert abs(result.specs['capacitance_farads'] - 0.0000001) < 1e-10
    assert result.specs['capacitance_str'] == "0.1μF"
    assert result.specs['voltage'] == 50
    assert result.specs['type'] == "ceramic"
    assert "0.1μF" in result.tags
    print("✅ 0.1μF capacitor parsed correctly")
    
    # Test 100nF capacitor
    result = parser.parse("100nF capacitor", "")
    assert result.category == "capacitor"
    assert abs(result.specs['capacitance_farads'] - 0.0000001) < 1e-10
    assert result.specs['capacitance_str'] == "100nF"
    print("✅ 100nF capacitor parsed correctly")
    
    # Test electrolytic capacitor
    result = parser.parse("220μF electrolytic capacitor 25V", "")
    assert result.category == "capacitor"
    assert result.specs['type'] == "electrolytic"
    assert result.specs['voltage'] == 25
    print("✅ 220μF electrolytic capacitor parsed correctly")


def test_ic_packages():
    """Test parsing IC packages"""
    parser = SpecificationParser()
    
    # Test 0805 SMD
    result = parser.parse("0805 SMD resistor", "")
    assert result.category == "electronics"
    assert result.specs['package'] == "0805"
    assert "0805" in result.tags
    assert "smd" in result.tags
    print("✅ 0805 package parsed correctly")
    
    # Test SOT-23
    result = parser.parse("SOT-23 transistor", "")
    assert result.category == "electronics"
    assert result.specs['package'] == "SOT-23"
    print("✅ SOT-23 package parsed correctly")


def test_materials():
    """Test material extraction"""
    parser = SpecificationParser()
    
    # Test stainless steel
    result = parser.parse("M6x40 stainless steel bolt", "")
    assert "stainless" in result.tags
    print("✅ Stainless material detected")
    
    # Test brass
    result = parser.parse("Brass fitting 1/4 inch", "")
    assert "brass" in result.tags
    print("✅ Brass material detected")
    
    # Test plastic
    result = parser.parse("Plastic spacer 10mm", "")
    assert "plastic" in result.tags
    print("✅ Plastic material detected")


def test_dimensions():
    """Test dimension parsing"""
    parser = SpecificationParser()
    
    # Test LxWxH
    result = parser.parse("Box 100x50x30mm", "")
    assert result.specs['length'] == 100
    assert result.specs['width'] == 50
    assert result.specs['height'] == 30
    assert result.specs['unit'] == 'mm'
    print("✅ 3D dimensions parsed correctly")
    
    # Test LxW
    result = parser.parse("Sheet 200x150mm", "")
    assert result.specs['length'] == 200
    assert result.specs['width'] == 150
    print("✅ 2D dimensions parsed correctly")


def test_complex_descriptions():
    """Test complex real-world descriptions"""
    parser = SpecificationParser()
    
    # Test complex screw description
    result = parser.parse("Pan head phillips screw, M6x50mm, stainless steel, A2-70 grade", "")
    assert result.category == "fastener"
    assert result.specs['thread_size'] == "M6"
    assert result.specs['length_mm'] == 50.0
    assert result.specs['head_type'] == "pan head"
    assert result.specs['drive'] == "phillips"
    assert "stainless" in result.tags
    assert result.confidence > 0.8
    print("✅ Complex screw description parsed correctly")
    
    # Test complex resistor description
    result = parser.parse("Metal film resistor, 4.7kΩ ±1%, 1/4W, axial package", "")
    assert result.category == "resistor"
    assert result.specs['resistance_ohms'] == 4700
    assert result.specs['tolerance'] == "1%"
    assert result.specs['wattage'] == "1/4W"
    print("✅ Complex resistor description parsed correctly")


def test_unit_conversion():
    """Test unit conversion functionality"""
    parser = SpecificationParser()
    
    # Test mm to inch
    result = parser.standardize_unit(25.4, 'mm', 'in')
    assert abs(result - 1.0) < 0.01
    print("✅ mm to inch conversion correct")
    
    # Test inch to mm
    result = parser.standardize_unit(1.0, 'in', 'mm')
    assert abs(result - 25.4) < 0.01
    print("✅ inch to mm conversion correct")
    
    # Test kg to lb
    result = parser.standardize_unit(1.0, 'kg', 'lb')
    assert abs(result - 2.20462) < 0.01
    print("✅ kg to lb conversion correct")


def run_all_tests():
    """Run all parser tests"""
    print("\n" + "="*60)
    print("Running SpecificationParser Tests (Phase 3)")
    print("="*60 + "\n")
    
    try:
        test_metric_fasteners()
        print()
        test_imperial_fasteners()
        print()
        test_resistors()
        print()
        test_capacitors()
        print()
        test_ic_packages()
        print()
        test_materials()
        print()
        test_dimensions()
        print()
        test_complex_descriptions()
        print()
        test_unit_conversion()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
