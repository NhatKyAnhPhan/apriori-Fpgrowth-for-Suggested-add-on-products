#!/usr/bin/env python3
"""
Test script để kiểm tra xem Apriori, FP-Growth, và CF đều hoạt động.
Chạy: python test_algorithms.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.algorithms.rule_engine import rule_engine
from backend.algorithms.collaborative_filtering import cf_engine

def test_algorithms():
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("TEST ALGORITHMS")
        print("=" * 60)
        
        # Check rules loaded
        print(f"\n✅ Apriori rules loaded: {len(rule_engine.apriori_rules)}")
        print(f"✅ FP-Growth rules loaded: {len(rule_engine.fpgrowth_rules)}")
        
        if rule_engine.apriori_rules:
            print(f"   Sample Apriori rule: {rule_engine.apriori_rules[0]}")
        
        # Check CF
        cf_engine.ensure_loaded()
        print(f"✅ CF users loaded: {len(cf_engine.user_items)}")
        print(f"✅ CF products loaded: {len(cf_engine.item_users)}")
        
        # Test with sample cart
        print("\n" + "=" * 60)
        print("TEST RECOMMENDATIONS WITH SAMPLE CART")
        print("=" * 60)
        
        test_carts = [
            ["ALARM CLOCK BAKELIKE RED", "DOLLY GIRL LUNCH BOX"],
            ["ALARM CLOCK BAKELIKE PINK"],
            ["GARDENERS KNEELING PAD CUP OF TEA"],
        ]
        
        for cart in test_carts:
            print(f"\n📦 Testing with cart: {cart}")
            print("-" * 60)
            
            # Test Apriori
            print("\n  🎯 APRIORI:")
            apriori_result = rule_engine.recommend(cart, method="apriori", top_n=3)
            print(f"     Results: {len(apriori_result)} items")
            if apriori_result:
                for i, r in enumerate(apriori_result[:2]):
                    print(f"     {i+1}. {r['product_id']} (conf={r['confidence']}, lift={r['lift']})")
            else:
                print("     ⚠️ NO RESULTS")
            
            # Test FP-Growth
            print("\n  🎯 FP-GROWTH:")
            fpg_result = rule_engine.recommend(cart, method="fpgrowth", top_n=3)
            print(f"     Results: {len(fpg_result)} items")
            if fpg_result:
                for i, r in enumerate(fpg_result[:2]):
                    print(f"     {i+1}. {r['product_id']} (conf={r['confidence']}, lift={r['lift']})")
            else:
                print("     ⚠️ NO RESULTS")
            
            # Test CF
            print("\n  🎯 COLLABORATIVE FILTERING:")
            cf_result = rule_engine.recommend(cart, method="collab", top_n=3)
            print(f"     Results: {len(cf_result)} items")
            if cf_result:
                for i, r in enumerate(cf_result[:2]):
                    print(f"     {i+1}. {r['product_id']} (conf={r['confidence']}, lift={r['lift']})")
            else:
                print("     ⚠️ NO RESULTS")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    test_algorithms()
