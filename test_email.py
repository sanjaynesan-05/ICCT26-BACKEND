"""
Email Testing Script for ICCT26 Cricket Tournament Registration API
This script helps you test the email functionality without making API calls
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Import email functions from main.py
try:
    from main import (
        send_confirmation_email,
        create_email_template_team,
        SMTP_USERNAME,
        SMTP_PASSWORD
    )
except ImportError as e:
    print(f"❌ Error importing from main.py: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def test_smtp_connection():
    """Test SMTP connection and credentials"""
    print("=" * 60)
    print("🔧 Testing SMTP Configuration")
    print("=" * 60)
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("❌ SMTP credentials not configured!")
        print("\nPlease add the following to your .env file:")
        print("SMTP_SERVER=smtp.gmail.com")
        print("SMTP_PORT=587")
        print("SMTP_USERNAME=your-email@gmail.com")
        print("SMTP_PASSWORD=your-app-password")
        print("SMTP_FROM_EMAIL=your-email@gmail.com")
        print("SMTP_FROM_NAME=ICCT26 Cricket Tournament")
        return False
    
    print(f"✓ SMTP Username: {SMTP_USERNAME}")
    print(f"✓ SMTP Password: {'*' * len(SMTP_PASSWORD)} (configured)")
    return True

def test_team_email():
    """Test team registration email"""
    print("\n" + "=" * 60)
    print("📧 Testing Team Registration Email")
    print("=" * 60)
    
    # Get recipient email
    to_email = input("\nEnter recipient email address (or press Enter to use SMTP_USERNAME): ").strip()
    if not to_email:
        to_email = SMTP_USERNAME
    
    print(f"\n📬 Sending test email to: {to_email}")
    
    # Sample team registration data
    team_data = {
        'captain': {'name': 'John Doe', 'email': to_email, 'phone': '+919876543210'},
        'teamName': 'Test Cricket Team',
        'churchName': 'CSI St. Peter\'s Church',
        'captainEmail': to_email,
        'captainPhone': '+919876543210'
    }
    
    players = [
        {'name': 'Player 1', 'age': 25, 'role': 'Batsman', 'phone': '+919876543211'},
        {'name': 'Player 2', 'age': 24, 'role': 'Bowler', 'phone': '+919876543212'},
        {'name': 'Player 3', 'age': 26, 'role': 'All-Rounder', 'phone': '+919876543213'}
    ]
    
    team_id = "ICCT26-TEST"
    
    # Create email template
    html_content = create_email_template_team(team_data, team_id, players)
    
    # Send email
    result = send_confirmation_email(
        to_email=to_email,
        subject="✅ ICCT26 Team Registration Confirmed [TEST]",
        html_content=html_content
    )
    
    if result['success']:
        print("\n✅ Team registration email sent successfully!")
        print(f"📬 Check inbox: {to_email}")
        print("💡 Tip: Check spam folder if you don't see it")
    else:
        print(f"\n❌ Failed to send email: {result['message']}")
    
    return result['success']

def test_external_email():
    """Test external participant email (same as team email for now)"""
    return test_team_email()

def save_template_preview():
    """Save HTML templates to files for preview"""
    print("\n" + "=" * 60)
    print("💾 Saving Email Template Previews")
    print("=" * 60)
    
    # Team registration template
    team_data = {
        'captain': {'name': 'John Doe', 'email': 'john.doe@example.com', 'phone': '+919876543210'},
        'teamName': 'Test Cricket Team',
        'churchName': 'CSI St. Peter\'s Church',
        'captainEmail': 'john.doe@example.com',
        'captainPhone': '+919876543210'
    }
    
    players = [
        {'name': 'Player 1', 'age': 25, 'role': 'Batsman', 'phone': '+919876543211'},
        {'name': 'Player 2', 'age': 24, 'role': 'Bowler', 'phone': '+919876543212'},
        {'name': 'Player 3', 'age': 26, 'role': 'All-Rounder', 'phone': '+919876543213'}
    ]
    
    team_id = "ICCT26-001"
    
    team_html = create_email_template_team(team_data, team_id, players)
    with open('email_template_team_preview.html', 'w', encoding='utf-8') as f:
        f.write(team_html)
    print("✓ Saved: email_template_team_preview.html")
    
    print("\n💡 Open this HTML file in your browser to preview the email template!")

def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("📧 ICCT26 Cricket Tournament Email Testing Tool")
    print("=" * 60)
    
    # Test SMTP configuration
    if not test_smtp_connection():
        print("\n⚠️  Please configure SMTP settings in .env file first.")
        print("See the SMTP configuration guide above.")
        return
    
    # Menu
    while True:
        print("\n" + "=" * 60)
        print("Choose an option:")
        print("=" * 60)
        print("1. Test Team Registration Email")
        print("2. Test External Email (same as team)")
        print("3. Test Both Emails")
        print("4. Save Template Preview (HTML file)")
        print("5. Exit")
        print("=" * 60)
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            test_team_email()
        elif choice == '2':
            test_external_email()
        elif choice == '3':
            test_team_email()
            test_external_email()
        elif choice == '4':
            save_template_preview()
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-5.")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
