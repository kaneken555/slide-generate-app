#!/bin/bash
# examples/test_api_with_curl.sh
#
# Test FastAPI server with curl

set -e

API_BASE="http://localhost:8000"

echo "======================================================================"
echo "FastAPI Server Test with curl"
echo "======================================================================"
echo ""

# Test 1: Health check
echo "[Test 1] Health Check"
echo "----------------------------------------------------------------------"
echo "Request: GET $API_BASE/health"
echo ""
curl -s "$API_BASE/health" | python -m json.tool
echo ""
echo ""

# Test 2: Create slides
echo "[Test 2] Create Slides (POST /api/v1/slides)"
echo "----------------------------------------------------------------------"
echo "Request: POST $API_BASE/api/v1/slides"
echo '{"topic": "FastAPI Basics", "n_slides": 5, "language": "Japanese"}'
echo ""

RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/slides" \
  -H "Content-Type: application/json" \
  -d '{"topic": "FastAPI Basics", "n_slides": 5, "language": "Japanese"}')

echo "$RESPONSE" | python -m json.tool
JOB_ID=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo ""
echo "Job ID: $JOB_ID"
echo ""
echo ""

# Test 3: Poll for status
echo "[Test 3] Poll Job Status (GET /api/v1/slides/{job_id})"
echo "----------------------------------------------------------------------"
echo "Polling for job completion..."
echo ""

MAX_ATTEMPTS=60
ATTEMPT=0
STATUS="pending"

while [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; do
  ATTEMPT=$((ATTEMPT + 1))
  echo "Attempt $ATTEMPT: Checking status..."

  STATUS_RESPONSE=$(curl -s "$API_BASE/api/v1/slides/$JOB_ID")
  STATUS=$(echo "$STATUS_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['status'])")

  echo "  Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    echo ""
    echo "======================================================================"
    echo "JOB COMPLETED!"
    echo "======================================================================"
    echo ""
    echo "$STATUS_RESPONSE" | python -m json.tool
    echo ""
    break
  elif [ "$STATUS" = "failed" ]; then
    echo ""
    echo "======================================================================"
    echo "JOB FAILED!"
    echo "======================================================================"
    echo ""
    echo "$STATUS_RESPONSE" | python -m json.tool
    echo ""
    break
  else
    sleep 2
  fi
done

if [ "$ATTEMPT" -ge "$MAX_ATTEMPTS" ]; then
  echo ""
  echo "======================================================================"
  echo "TIMEOUT: Job did not complete within time limit"
  echo "======================================================================"
  echo ""
fi

# Test 4: Get stats
echo "[Test 4] Get Statistics (GET /api/v1/stats)"
echo "----------------------------------------------------------------------"
echo "Request: GET $API_BASE/api/v1/stats"
echo ""
curl -s "$API_BASE/api/v1/stats" | python -m json.tool
echo ""
echo ""

echo "======================================================================"
echo "All tests completed!"
echo "======================================================================"
