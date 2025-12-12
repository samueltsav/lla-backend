from svix.webhooks import Webhook
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from user_service_config.django import base
from django.contrib.auth import get_user_model
import json

User = get_user_model()


@method_decorator(csrf_exempt, name="dispatch")
class ClerkWebhook(View):
    """
    Handle Clerk webhook events
    """
    webhook_secret = getattr(base, "CLERK_WEBHOOK_SECRET", "")
    
    def post(self, request, *args, **kwargs):
        """
        Process incoming webhook from Clerk
        """
        try:
            # Get Svix headers
            svix_user_id = request.headers.get("svix-user_id")
            svix_timestamp = request.headers.get("svix-timestamp")
            svix_signature = request.headers.get("svix-signature")
            
            if not all([svix_user_id, svix_timestamp, svix_signature]):
                return HttpResponseBadRequest("Missing svix headers")
            
            # Verify webhook signature
            payload = request.body
            wh = Webhook(self.webhook_secret)
            
            try:
                msg = wh.verify(payload, {
                    "svix-user_id": svix_user_id,
                    "svix-timestamp": svix_timestamp,
                    "svix-signature": svix_signature,
                })
            except Exception as e:
                return HttpResponseBadRequest(f"Webhook verification failed: {str(e)}")
            
            # Parse event
            event_type = msg.get("type")
            event_data = msg.get("data", {})
            
            # Route to appropriate handler
            handler = self.get_event_handler(event_type)
            if handler:
                handler(event_data)
            
            return JsonResponse({"status": "success", "event_type": event_type})
            
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invaluser_id JSON")
        except Exception as e:
            return HttpResponseBadRequest(f"Error processing webhook: {str(e)}")
    
    def get_event_handler(self, event_type):
        """
        Map event types to handler methods
        """
        handlers = {
            "user.created": self.handle_user_created,
            "user.updated": self.handle_user_updated,
            "user.deleted": self.handle_user_deleted,
            "session.created": self.handle_session_created,
            "session.ended": self.handle_session_ended,
        }
        return handlers.get(event_type)
    
    def handle_user_created(self, user_data):
        """Handle user.created event"""
        user_id = user_data.get("user_id")
        email_addresses = user_data.get("email_addresses", [])
        email = email_addresses[0].get("email_address", "") if email_addresses else ""
        
        user, created = User.objects.get_or_create(
            user_id=user_id,
            defaults={
                "email": email,
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
            }
        )
        
        if created:
            print(f"Created new user: {user.username}")
    
    def handle_user_updated(self, user_data):
        """Handle user.updated event"""
        user_id = user_data.get("user_id")
        
        try:
            user = User.objects.get(user_id=user_id)
            email_addresses = user_data.get("email_addresses", [])
            email = email_addresses[0].get("email_address", "") if email_addresses else ""
            
            user.email = email
            user.first_name = user_data.get("first_name", "")
            user.last_name = user_data.get("last_name", "")
            user.save()
            
            print(f"Updated user: {user.username}")
        except User.DoesNotExist:
            print(f"User with user_id {user_id} not found")
    
    def handle_user_deleted(self, user_data):
        """Handle user.deleted event"""
        user_id = user_data.get("user_id")
        
        try:
            user = User.objects.get(user_id=user_id)
            email = user.email
            user.delete()
            print(f"Deleted user: {email}")
        except User.DoesNotExist:
            print(f"User with user_id {user_id} not found")
    
    def handle_session_created(self, session_data):
        """Handle session.created event"""
        # Add custom logic for session creation if needed
        print(f"Session created for user: {session_data.get("user_id")}")
    
    def handle_session_ended(self, session_data):
        """Handle session.ended event"""
        # Add custom logic for session end if needed
        print(f"Session ended for user: {session_data.get("user_id")}")