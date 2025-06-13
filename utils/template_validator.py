import pandas as pd

def validate_template(file_path, expected_fields):
    df = pd.read_excel(file_path)

    # Example check: field names match
    template_fields = df.columns.tolist()
    missing_fields = [field for field in expected_fields if field not in template_fields]

    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
        return False, missing_fields
    else:
        print("✅ Template fields validated.")
        return True, []
