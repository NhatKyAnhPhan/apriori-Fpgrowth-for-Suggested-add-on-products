#!/usr/bin/env python3
"""
Test CSV parsing logic locally without full app import.
"""

import csv
import os
import ast

def _parse_itemset(value: str) -> frozenset:
    """Convert CSV string (comma or Python list format) to frozenset."""
    if not value:
        return frozenset()
    val_str = str(value).strip()
    # Old format: "['MILK', 'BREAD']"
    if val_str.startswith('[') and val_str.endswith(']'):
        try:
            parsed = ast.literal_eval(val_str)
            return frozenset(item.strip().upper() for item in parsed)
        except Exception:
            pass
    # New format: "MILK,BREAD"
    return frozenset(item.strip().upper() for item in val_str.split(',') if item.strip())

def test_csv_parsing():
    csv_path = r"c:\kpdl\do_an_khai_pha\backend\precomputed\apriori_rules.csv"
    
    print("=" * 60)
    print("TEST CSV PARSING")
    print("=" * 60)
    print(f"\nReading: {csv_path}")
    print(f"File exists: {os.path.exists(csv_path)}\n")
    
    if not os.path.exists(csv_path):
        print("❌ File not found!")
        return
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rules = list(reader)
    
    print(f"✅ Loaded {len(rules)} rules from CSV\n")
    
    # Test first 5 rules
    for i, rule in enumerate(rules[:5]):
        ant_str = rule.get('antecedents', '')
        con_str = rule.get('consequents', '')
        
        ant_parsed = _parse_itemset(ant_str)
        con_parsed = _parse_itemset(con_str)
        
        print(f"Rule {i}:")
        print(f"  antecedents_str: {repr(ant_str)}")
        print(f"  antecedents_parsed: {ant_parsed}")
        print(f"  consequents_str: {repr(con_str)}")
        print(f"  consequents_parsed: {con_parsed}")
        print()
    
    # Test matching logic
    print("=" * 60)
    print("TEST MATCHING LOGIC")
    print("=" * 60)
    
    test_carts = [
        ['ALARM CLOCK BAKELIKE RED'],
        ['DOLLY GIRL LUNCH BOX'],
        ['ALARM CLOCK BAKELIKE RED', 'DOLLY GIRL LUNCH BOX'],
    ]
    
    for cart in test_carts:
        user_cart = frozenset(str(item).strip().upper() for item in cart)
        print(f"\nCart: {cart}")
        print(f"Parsed cart: {user_cart}")
        
        matches = 0
        for i, rule in enumerate(rules[:10]):
            ant = _parse_itemset(rule['antecedents'])
            con = _parse_itemset(rule['consequents'])
            
            if ant and ant.issubset(user_cart):
                matches += 1
                print(f"  ✓ Rule {i}: {ant} -> {con}")
        
        print(f"  Total matches: {matches}")

if __name__ == "__main__":
    test_csv_parsing()
