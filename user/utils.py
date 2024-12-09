from django.core.mail import send_mail
import requests

def send_otp_email(user):
    """
    Sends an OTP to the user's email address.

    Args:
        user: The user object with email and OTP fields.
    """
    subject = "Your OTP Verification Code"
    message = f"""
    Hello {user.first_name or "User"},
    
    Your OTP code is: {user.otp_code}
    
    Please use this code to complete your verification. This OTP is valid for 5 minutes.
    
    Thank you!
    """
    from_email = "your_email@example.com"  
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

def geocode_address(address):
    """
    Calls the Google Geocoding API to fetch latitude and longitude for a given address.
    """
    api_key = "AIzaSyD0RqtfT324DAtkXkeH3P8NpaGf-Hc28vU"  # Replace with your actual API key
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            return None, None
    return None, None
