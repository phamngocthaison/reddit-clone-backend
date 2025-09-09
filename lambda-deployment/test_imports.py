def handler(event, context):
    try:
        import pydantic
        print(f"Pydantic version: {pydantic.VERSION}")
        
        from pydantic import EmailStr
        print("EmailStr imported successfully")
        
        import email_validator
        print("email_validator imported successfully")
        
        return {
            "statusCode": 200,
            "body": "All imports successful"
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
