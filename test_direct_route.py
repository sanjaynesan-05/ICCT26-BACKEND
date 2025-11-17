"""
Direct test of registration route without HTTP - diagnose import issue
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("🔍 DIRECT ROUTE IMPORT TEST")
print("=" * 70)

try:
    print("\n1️⃣ Testing team_id_generator import directly...")
    from app.utils.team_id_generator import generate_sequential_team_id, generate_player_id
    print("   ✅ Success: team_id_generator imported")
    print(f"   - generate_sequential_team_id: {generate_sequential_team_id}")
    print(f"   - generate_player_id: {generate_player_id}")
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n2️⃣ Testing registration_cloudinary route import...")
    from app.routes import registration_cloudinary
    print("   ✅ Success: registration_cloudinary imported")
    print(f"   - Router: {registration_cloudinary.router}")
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n3️⃣ Checking if route module has the function...")
    from app.routes import registration_cloudinary
    # Check if module can see the function
    import inspect
    source = inspect.getsource(registration_cloudinary.register_team)
    if "generate_sequential_team_id" in source:
        print("   ✅ Function name found in route source code")
    else:
        print("   ❌ Function name NOT found in route source code")
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n4️⃣ Testing if route can access the function...")
    from app.routes.registration_cloudinary import generate_sequential_team_id as route_func
    print(f"   ✅ Route CAN import the function: {route_func}")
except Exception as e:
    print(f"   ⚠️ Route CANNOT import: {e}")
    # This is expected since it's not defined IN the route file

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
