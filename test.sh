#!/bin/bash

# --- Configuration ---
ALATION_URL="https://northstar.mtse.alationcloud.com"
ACCESS_TOKEN="aDTzfZ38GCBMPfnX9mBPQ3vnaEtPVanyQqzGU-SMVLI"
USER_EMAIL_TO_SEARCH="alex.davis@alation.com" # e.g., alex.davis@alation.com

# --- API Call ---
echo "Attempting to search for user: ${USER_EMAIL_TO_SEARCH}"
echo "API URL: ${ALATION_URL}/integration/v1/user/search?q=${USER_EMAIL_TO_SEARCH}&limit=100"

curl --request GET \
     --url "${ALATION_URL}/integration/v1/user/search?q=${USER_EMAIL_TO_SEARCH}&limit=100" \
     --header "TOKEN: ${ACCESS_TOKEN}" \
     --header "accept: application/json" \
     --fail \
     --show-error \
     --silent \
     | jq .

echo ""
echo "--- END OF RESPONSE ---"