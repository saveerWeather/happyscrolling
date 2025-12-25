#!/bin/bash

echo "Testing Busyplates Login Flow"
echo "=============================="
echo ""

# Test 1: Login
echo "1. Testing login endpoint..."
RESPONSE=$(curl -s -c /tmp/cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"sjain136@icloud.com","password":"jcpsSJ2688!"}')

echo "Response: $RESPONSE"
echo ""

# Check if login was successful
if echo "$RESPONSE" | grep -q '"id"'; then
  echo "✓ Login successful!"
  USER_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | cut -d':' -f2)
  echo "  User ID: $USER_ID"
else
  echo "✗ Login failed"
  exit 1
fi

echo ""

# Test 2: Check /me endpoint with cookie
echo "2. Testing /api/auth/me with session cookie..."
ME_RESPONSE=$(curl -s -b /tmp/cookies.txt http://localhost:8000/api/auth/me)
echo "Response: $ME_RESPONSE"
echo ""

if echo "$ME_RESPONSE" | grep -q '"id"'; then
  echo "✓ Session cookie works!"
else
  echo "✗ Session validation failed"
  exit 1
fi

echo ""
echo "=============================="
echo "All tests passed! ✓"
echo ""
echo "Now try logging in at: http://localhost:3000/login"
echo "  Email: sjain136@icloud.com"
echo "  Password: jcpsSJ2688!"
