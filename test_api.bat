@echo off
REM Test API endpoints

echo ========== TEST 1: Check Rules Loaded ==========
curl -s http://localhost:5000/api/debug/rules | jq .
echo.

echo ========== TEST 2: Apriori with Simple Cart ==========
curl -s -X POST http://localhost:5000/api/recommend ^
  -H "Content-Type: application/json" ^
  -d "{\"items\": [\"ALARM CLOCK BAKELIKE RED\"], \"method\": \"apriori\"}" | jq .
echo.

echo ========== TEST 3: FP-Growth with Simple Cart ==========
curl -s -X POST http://localhost:5000/api/recommend ^
  -H "Content-Type: application/json" ^
  -d "{\"items\": [\"ALARM CLOCK BAKELIKE RED\"], \"method\": \"fpgrowth\"}" | jq .
echo.

echo ========== TEST 4: CF with Simple Cart ==========
curl -s -X POST http://localhost:5000/api/recommend ^
  -H "Content-Type: application/json" ^
  -d "{\"items\": [\"ALARM CLOCK BAKELIKE RED\"], \"method\": \"collab\"}" | jq .
echo.
