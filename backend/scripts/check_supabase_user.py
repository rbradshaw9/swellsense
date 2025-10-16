"""
Check if a user exists in Supabase and verify their credentials
Usage: python scripts/check_supabase_user.py --email rbradshaw@gmail.com
"""
import os
import sys
import asyncio
import argparse
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_user(email: str):
    """Check if user exists and list their details"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment")
        print("\nRequired environment variables:")
        print("  - SUPABASE_URL: Your Supabase project URL")
        print("  - SUPABASE_SERVICE_KEY: Your Supabase service role key (secret!)")
        return
    
    print(f"🔍 Checking Supabase for user: {email}")
    print(f"📍 Supabase URL: {supabase_url}")
    print()
    
    try:
        # Create Supabase client with service role key (full access)
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        # Query auth.users table using admin API
        print("🔐 Querying Supabase Auth...")
        
        # Use admin API to list users
        response = supabase.auth.admin.list_users()
        
        # Find the user by email
        user = None
        for u in response:
            if hasattr(u, 'email') and u.email == email:
                user = u
                break
        
        if not user:
            print(f"❌ User not found: {email}")
            print("\nTo create this user:")
            print("1. Go to your Supabase dashboard > Authentication > Users")
            print("2. Click 'Invite user' or 'Add user'")
            print(f"3. Enter email: {email}")
            print("4. Set a password")
            print("5. Confirm email if required")
            return
        
        print(f"✅ User found!")
        print(f"\n📧 Email: {user.email}")
        print(f"🆔 User ID: {user.id}")
        print(f"📅 Created: {user.created_at}")
        print(f"🔓 Email confirmed: {user.email_confirmed_at is not None}")
        print(f"🕐 Last sign in: {user.last_sign_in_at}")
        
        # Check if email is confirmed
        if not user.email_confirmed_at:
            print("\n⚠️  WARNING: Email not confirmed!")
            print("The user needs to confirm their email before they can log in.")
            print("\nTo fix:")
            print("1. Go to Supabase dashboard > Authentication > Users")
            print(f"2. Find {email}")
            print("3. Click the three dots menu > Confirm email")
        
        # Check user metadata
        if hasattr(user, 'user_metadata') and user.user_metadata:
            print(f"\n👤 User metadata:")
            for key, value in user.user_metadata.items():
                print(f"   - {key}: {value}")
        
        # Check app metadata
        if hasattr(user, 'app_metadata') and user.app_metadata:
            print(f"\n🔧 App metadata:")
            for key, value in user.app_metadata.items():
                print(f"   - {key}: {value}")
        
        print("\n✅ User exists and should be able to log in!")
        print(f"\nTo test login in frontend:")
        print(f"1. Go to https://swellsense.app/login")
        print(f"2. Enter email: {email}")
        print(f"3. Enter the password you set")
        
    except Exception as e:
        print(f"❌ Error querying Supabase: {str(e)}")
        print(f"\nFull error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if user exists in Supabase")
    parser.add_argument("--email", required=True, help="User email to check")
    
    args = parser.parse_args()
    
    asyncio.run(check_user(args.email))
