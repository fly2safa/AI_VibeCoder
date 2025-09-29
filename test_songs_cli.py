#!/usr/bin/env python3
"""
Quick test script for the Songs CLI application
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def test_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB connection...")
    
    # Load environment variables
    load_dotenv()
    
    project_db_url = os.getenv('project_db_url')
    if not project_db_url:
        print("❌ project_db_url not found in environment variables")
        print("Please create a .env file with your MongoDB connection string")
        return False
    
    print(f"✅ Found MongoDB URL: {project_db_url[:20]}...")
    return True

def run_test_commands():
    """Run test commands to verify the CLI works"""
    print("\n🧪 Running test commands...")
    
    test_user = "test_user"
    
    commands = [
        # Add a test song
        f"python songs_cli.py --user {test_user} add --title 'Test Song' --artist 'Test Artist' --genre 'Test' --year 2024",
        
        # List songs
        f"python songs_cli.py --user {test_user} list",
        
        # Search songs
        f"python songs_cli.py --user {test_user} search 'Test'",
        
        # Show history
        f"python songs_cli.py --user {test_user} history"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n--- Test {i}: {cmd.split()[2]} ---")
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Success")
                if result.stdout:
                    print(result.stdout)
            else:
                print("❌ Failed")
                if result.stderr:
                    print(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("⏰ Command timed out")
        except Exception as e:
            print(f"❌ Error running command: {e}")

def main():
    """Main test function"""
    print("🎵 Songs CLI Test Suite")
    print("=" * 40)
    
    # Test environment setup
    if not test_connection():
        sys.exit(1)
    
    # Check if main script exists
    if not os.path.exists('songs_cli.py'):
        print("❌ songs_cli.py not found in current directory")
        sys.exit(1)
    
    # Run test commands
    run_test_commands()
    
    print("\n🎉 Test suite completed!")
    print("\nTo use the CLI manually:")
    print("1. Make sure your .env file has the correct project_db_url")
    print("2. Run: python songs_cli.py --user YourName add --title 'Song Title' --artist 'Artist Name'")

if __name__ == "__main__":
    main()