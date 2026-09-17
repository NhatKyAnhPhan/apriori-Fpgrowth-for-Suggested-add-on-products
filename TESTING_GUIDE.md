# Testing Guide - Apriori & CF Recommendations

## Overview
You reported that only FP-Growth shows results, while Apriori and CF return empty. I've debugged and made several improvements:

✅ **Fixed Issues:**
1. Results not resetting when switching algorithms (Frontend)
2. CF lazy loading to avoid app context errors
3. Added detailed logging to debug flow

## How to Test

### Step 1: Start Backend Server
```bash
cd c:\kpdl\do_an_khai_pha\backend
python app.py
```
Watch the console for messages. It should show:
```
🔄 [RuleEngine] Đã cập nhật và đồng bộ luật mới thành công (Thuần Python)!
```

### Step 2: Verify Rules Loaded
Open browser and visit: http://localhost:5000/api/debug/rules

Should return:
```json
{
  "apriori_count": 52,
  "fpgrowth_count": 76,
  "apriori_sample": [...],
  "fpgrowth_sample": [...]
}
```

**If this shows 0 count, rules aren't loading - that's the issue!**

### Step 3: Test Frontend
1. Go to http://localhost:3000 (Frontend should already be running)
2. Add some products to cart (use "Thêm vào giỏ" button)
3. Go to Compare page (/compare)
4. You should see "💡 Đã tự động đồng bộ X sản phẩm từ giỏ hàng"

### Step 4: Test Each Algorithm
1. **Click "Apriori" button** (should turn dark)
2. **Click "Phân tích luật kết hợp" button**
3. Watch backend console for logs like:
   ```
   🔍 [RuleEngine.recommend] method=apriori, cart_items=[...], user_cart={...}
   📊 [RuleEngine] method=apriori, loaded 52 rules
   ✅ [RuleEngine] Matched X/52 rules, found Y candidates
   📦 [RuleEngine] Returning Z recommendations
   ```

**What to check:**
- Is "Matched X/52 rules" showing X > 0? If X=0, rules don't match cart items
- Are recommendations appearing in UI?

4. **Repeat for FP-Growth** - same process
5. **Repeat for CF + FP-G** - watch for CF-specific logs

### Step 5: Troubleshoot with Console & Network Tab
1. Open **Browser DevTools** (F12)
2. Go to **Network** tab
3. Click "Phân tích" button and watch:
   - Request URL, method, body
   - Response status (should be 200)
   - Response body (should have "recommendations" array)
4. Go to **Console** tab - watch for any errors

### Step 6: Test with cURL (If Backend Issue)
```bash
# Test with simple cart
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"items": ["ALARM CLOCK BAKELIKE RED"], "method": "apriori"}'

# Expected response:
# {
#   "recommendations": [...],
#   "count": X
# }
```

## Common Issues & Solutions

### Issue 1: Rules show 0 count
**Problem:** Rules files not found or corrupted
**Solution:** 
- Check if files exist: `backend/precomputed/apriori_rules.csv` and `fpgrowth_rules.csv`
- File should have 52+ lines for apriori, 76+ for fpgrowth
- Check line 1 is header: `antecedents,consequents,support,confidence,lift`

### Issue 2: Recommendations empty but rules loaded
**Problem:** Cart items don't match any rules
**Solution:**
- Check if you actually added products to cart
- Product names must be EXACT (case-insensitive but must be exact matches)
- Valid products from our data:
  - ALARM CLOCK BAKELIKE RED
  - ALARM CLOCK BAKELIKE GREEN
  - ALARM CLOCK BAKELIKE PINK
  - DOLLY GIRL LUNCH BOX
  - GARDENERS KNEELING PAD CUP OF TEA

### Issue 3: CF returns empty
**Problem:** Not enough data or CF logic issue
**Solution:**
- CF needs multiple users with purchase history
- If database is empty/fresh, CF won't work
- Check console for CF-specific logs

### Issue 4: Frontend shows loading forever
**Problem:** API call hanging
**Solution:**
- Check if backend is running
- Look at Network tab - is request pending or failing?
- Check backend console for errors

## What I Fixed

### Backend Changes
1. **algorithms/rule_engine.py**: Added logging for debugging
2. **algorithms/collaborative_filtering.py**: Fixed app context error with lazy loading
3. **api/recommend.py**: Added /api/debug/rules endpoint and request logging

### Frontend Changes  
1. **pages/ComparePage.jsx**: Fixed results not resetting when method changes

## Files to Check
- `backend/precomputed/apriori_rules.csv` - Should have 52 rules
- `backend/precomputed/fpgrowth_rules.csv` - Should have 76 rules
- `backend/algorithms/rule_engine.py` - Core logic
- `frontend/src/pages/ComparePage.jsx` - UI for Compare page

## Debug Logs You Should See

**When clicking Apriori + Phân tích:**
```
🔔 [API /recommend] REQUEST RECEIVED:
   method=apriori, top_n=5
   cart_items=['ALARM CLOCK BAKELIKE RED', ...]
🔍 [RuleEngine.recommend] method=apriori, ...
📊 [RuleEngine] method=apriori, loaded 52 rules
✅ [RuleEngine] Matched 2/52 rules, found 1 candidates
📦 [RuleEngine] Returning 1 recommendations
```

## Report Findings
After testing, please share:
1. Do rules load in /api/debug/rules? (Show count)
2. When you click Apriori & Phân tích, what does console show?
3. Does cart have products? (Check if "💡 Đã tự động đồng bộ X sản phẩm" shows)
4. What error messages appear in browser console (F12)?
