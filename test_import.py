"""Quick import test"""
import sys
print("Testing imports...")

try:
    from app.utils.team_id_generator import generate_sequential_team_id, generate_player_id
    print("✅ Direct import works")
    print(f"   generate_sequential_team_id: {generate_sequential_team_id}")
    print(f"   generate_player_id: {generate_player_id}")
except Exception as e:
    print(f"❌ Direct import failed: {e}")

try:
    from app.routes import registration_cloudinary
    print("✅ Route module imports successfully")
except Exception as e:
    print(f"❌ Route import failed: {e}")
    import traceback
    traceback.print_exc()
