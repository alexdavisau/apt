#!/bin/zsh

# Set your token and API URL here
token="YOUR_API_TOKEN"
api_url="YOUR_API_BASE_URL"

# Get folder listing
get_response=$(curl -s -L -X GET -H "Token: $token" -H "accept: application/json" -H "content-type: application/json" "$api_url")

# Process the response
if [ "$(echo "$get_response" | jq -r '. | type')" == "object" ]; then
    echo "Successfully retrieved folders listing"
    
    # Process each folder template
    for ct_id in $(echo "${get_response}" | jq -r '.folder_templates[].id'); do
        if [ -n "$ct_id" ]; then
            # Construct the template API URL
            ct_api_url="${api_url}/folder_templates/${ct_id}"
            
            # Get template details
            ct_get_response=$(curl -s -L -X GET -H "Token: $token" -H "accept: application/json" -H "content-type: application/json" "$ct_api_url")

            # Check the response
            if [ "$(echo "$ct_get_response" | jq -r '. | type')" == "object" ]; then
                # Get Folder Template Information
                echo -e "\tTemplate Name: $(echo "$ct_get_response" | jq -r '.title')"
                echo -e "\t\tBuilt-In & Custom Fields:"

                # Iterate through the fields
                for field in $(echo "${ct_get_response}" | jq -r '.fields[] | @base64'); do
                    _field_jq() {
                        echo "${field}" | base64 --decode | jq -r "${1}"
                    }

                    echo -e "\t\t\tField ID: $(_field_jq '.id')"
                    if [ "$(_field_jq '.builtin_name')" != "null" ]; then
                        echo -e "\t\t\t\tField Type: $(_field_jq '.field_type')"
                        echo -e "\t\t\t\tBuilt-In Name: $(_field_jq '.builtin_name')"
                    else
                        echo -e "\t\t\t\tField Type: $(_field_jq '.field_type')"
                        echo -e "\t\t\t\tSingular Name: $(_field_jq '.name_singular')"
                        echo -e "\t\t\t\tPlural Name: $(_field_jq '.name_plural')"
                    fi

                    echo -e "\t\t\t\tAllow Multiple: $(_field_jq '.allow_multiple')"
                    echo -e "\t\t\t\tAllowed Otypes: $(_field_jq '.allowed_otypes' | jq -c)"
                done
            else
                echo -e "\tFailed to retrieve folder template information: $(echo "$ct_get_response" | jq -r '.status_code')"
            fi
        fi
    done
else
    echo "Failed to retrieve folders listing: $(echo "$get_response" | jq -r '.status_code')"
fi

