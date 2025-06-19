import json
import redis
import os
from pathlib import Path
import jsonschema

def store_configs_in_redis():
    """Store agent configs in Redis with keys like agent|{filename}"""
    
    # Connect to Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()  # Test connection
        print("Connected to Redis successfully")
    except redis.ConnectionError:
        print("Error: Could not connect to Redis. Make sure Redis is running on localhost:6379")
        return
    
    # Get the configs directory
    configs_dir = Path(__file__).parent
    
    # Load the schema for validation
    schema_file = configs_dir / "agent_config_schema.json"
    try:
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        print("Loaded agent config schema for validation")
    except Exception as e:
        print(f"Error loading schema file: {e}")
        return
    
    # Check existing configs in Redis for validation issues
    print("\nChecking existing configs in Redis...")
    existing_agent_keys = r.keys("agent|*")
    invalid_stored_configs = []
    
    for key in existing_agent_keys:
        try:
            stored_content = r.get(key)
            if stored_content:
                # Parse JSON
                try:
                    stored_data = json.loads(stored_content)
                except json.JSONDecodeError as json_err:
                    print(f"⚠️  INVALID JSON in Redis key '{key}': {json_err}")
                    invalid_stored_configs.append(key)
                    continue
                
                # Validate against schema
                try:
                    jsonschema.validate(stored_data, schema)
                    print(f"✓ Redis key '{key}' passes validation")
                except jsonschema.ValidationError as schema_err:
                    print(f"⚠️  SCHEMA VIOLATION in Redis key '{key}': {schema_err.message}")
                    invalid_stored_configs.append(key)
                except jsonschema.SchemaError as schema_err:
                    print(f"⚠️  Schema error validating Redis key '{key}': {schema_err.message}")
                    invalid_stored_configs.append(key)
        except Exception as e:
            print(f"Error checking Redis key '{key}': {e}")
    
    if invalid_stored_configs:
        print(f"\n🚨 WARNING: Found {len(invalid_stored_configs)} invalid configs in Redis:")
        for key in invalid_stored_configs:
            print(f"   - {key}")
        
        # Ask user if they want to delete invalid configs
        while True:
            response = input("\nDo you want to delete these invalid configs from Redis? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                deleted_count = 0
                for key in invalid_stored_configs:
                    try:
                        r.delete(key)
                        print(f"Deleted invalid config: {key}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting {key}: {e}")
                print(f"\n✓ Deleted {deleted_count} invalid configs from Redis\n")
                break
            elif response in ['n', 'no']:
                print("Invalid configs left in Redis. Please manually correct them.\n")
                break
            else:
                print("Please enter 'y' or 'n'")
    else:
        print("✓ All existing configs in Redis are valid\n")
    
    # Find all JSON files (exclude schema, kv_store.json, and any other non-config files)
    json_files = [f for f in configs_dir.glob("*.json") 
                  if f.name not in ["agent_config_schema.json"]]
    
    print(f"Found {len(json_files)} config files to store")
    
    # Store each config file in Redis
    for json_file in json_files:
        filename_without_ext = json_file.stem
        key = f"agent|{filename_without_ext}"
        
        # Read the JSON file content
        try:
            with open(json_file, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {json_file.name}: {e}")
            continue
        
        # Parse and validate JSON syntax
        try:
            config_data = json.loads(content)
            print(f"✓ {json_file.name} contains valid JSON")
        except json.JSONDecodeError as json_err:
            print(f"✗ {json_file.name} contains invalid JSON: {json_err}")
            continue  # Skip this file and move to the next
        
        # Validate against schema
        try:
            jsonschema.validate(config_data, schema)
            print(f"✓ {json_file.name} passes schema validation")
        except jsonschema.ValidationError as schema_err:
            print(f"✗ {json_file.name} fails schema validation: {schema_err.message}")
            continue  # Skip this file and move to the next
        except jsonschema.SchemaError as schema_err:
            print(f"✗ Schema error: {schema_err.message}")
            continue
        
        # Store in Redis (only reached if all validations pass)
        try:
            r.set(key, content)
            print(f"Stored {json_file.name} as key: {key}")
        except Exception as e:
            print(f"Error storing {json_file.name} in Redis: {e}")
    
    print("\nStored configs in Redis:")
    # List all agent keys to verify
    agent_keys = r.keys("agent|*")
    for key in agent_keys:
        print(f"  {key}")

if __name__ == "__main__":
    store_configs_in_redis() 