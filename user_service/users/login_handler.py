import re
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .tasks import send_login_notification_email, send_suspicious_login_alert

logger = logging.getLogger(__name__)


class LoginNotificationHandler:
    def __init__(self, user, request):
        self.user = user
        self.request = request
        self.suspicious_indicators = [
            "unknown_location",
            "new_device", 
            "multiple_failed_attempts",
            "unusual_time",
            "vpn_detected",
            "tor_detected"
        ]
    
    def handle_login(self) -> Optional[str]:
        """Main entry point for handling login notifications."""
        user_data = {
            "username": self.user.username,
            "email": self.user.email,
        }
        request_data = {
            "x-forwarded-for": self.request.META.get("HTTP_X_FORWARDED_FOR"),
            "x-real-ip": self.request.META.get("HTTP_X_REAL_IP"),
            "remote-addr": self.request.META.get("REMOTE_ADDR"),
            "user_agent": self.request.META.get("HTTP_USER_AGENT", ""),
        }

        return self.handle_successful_login(user_data, request_data)

    def handle_successful_login(
        self, user_data: Dict[str, Any], request_data: Dict[str, Any]
    ) -> Optional[str]:
        try:
            # Extract login information
            login_info = self.extract_login_info(request_data)

            # Check if login is suspicious
            is_suspicious, suspicious_reasons = self.analyze_login_suspicion(
                user_data, login_info
            )

            if is_suspicious:
                # Send suspicious login alert
                task = send_suspicious_login_alert.delay(
                    user_data,
                    {
                        **login_info,
                        "suspicious_reasons": suspicious_reasons,
                    },
                )
                return task.id
            else:
                # Send regular login notification
                task = send_login_notification_email.delay(user_data, login_info)
                return task.id

        except Exception as e:
            logger.error(f"Error handling login notification: {str(e)}")
            return None

    def extract_login_info(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        ip_address = self.get_client_ip(request_data)
        user_agent = request_data.get("user_agent", "")

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "ip_address": ip_address,
            "location": self.get_location_from_ip(ip_address),
            "device_info": self.parse_device_info(user_agent),
            "browser": self.parse_browser_info(user_agent),
            "user_agent": user_agent,
        }

    def get_client_ip(self, request_data: Dict[str, Any]) -> str:
        """Get client IP address from request data."""
        for header in ["x-forwarded-for", "x-real-ip", "remote-addr"]:
            ip = request_data.get(header)
            if ip:
                return ip.split(",")[0].strip()  # handle multiple IPs
        return "Unknown"

    def get_location_from_ip(self, ip_address: str) -> str:
        if ip_address == "Unknown" or self.is_private_ip(ip_address):
            return "Unknown"

        try:
            response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    return f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
        except Exception as e:
            logger.warning(f"Failed to get location for IP {ip_address}: {str(e)}")

        return "Unknown"

    def is_private_ip(self, ip: str) -> bool:
        private_patterns = [
            r"^10\.",
            r"^192\.168\.",
            r"^172\.(1[6-9]|2\d|3[01])\.",
            r"^127\.",
            r"^::1$",
            r"^localhost$",
        ]
        return any(re.match(pattern, ip) for pattern in private_patterns)

    def parse_device_info(self, user_agent: str) -> str:
        if not user_agent:
            return "Unknown"

        ua = user_agent.lower()
        if "mobile" in ua or "android" in ua:
            return "Mobile Device"
        elif "tablet" in ua or "ipad" in ua:
            return "Tablet"
        elif "windows" in ua:
            return "Windows PC"
        elif "mac" in ua and "mobile" not in ua:
            return "Mac"
        elif "linux" in ua:
            return "Linux PC"
        return "Unknown Device"

    def parse_browser_info(self, user_agent: str) -> str:
        if not user_agent:
            return "Unknown"

        ua = user_agent.lower()
        if "chrome" in ua and "edge" not in ua:
            return "Chrome"
        elif "firefox" in ua:
            return "Firefox"
        elif "safari" in ua and "chrome" not in ua:
            return "Safari"
        elif "edge" in ua:
            return "Edge"
        elif "opera" in ua:
            return "Opera"
        return "Unknown Browser"

    def analyze_login_suspicion(
        self, user_data: Dict[str, Any], login_info: Dict[str, Any]
    ) -> tuple[bool, list]:
        suspicious_reasons = []

        if login_info["location"] == "Unknown":
            suspicious_reasons.append("Login from unknown location")

        ip = login_info["ip_address"]
        if self.is_tor_ip(ip):
            suspicious_reasons.append("Login through Tor network detected")
        elif self.is_vpn_ip(ip):
            suspicious_reasons.append("VPN or proxy usage detected")

        try:
            login_hour = datetime.strptime(
                login_info["timestamp"], "%Y-%m-%d %H:%M:%S UTC"
            ).hour
            if login_hour < 6 or login_hour > 23:
                suspicious_reasons.append("Login at unusual time")
        except Exception:
            pass

        return len(suspicious_reasons) > 0, suspicious_reasons

    def is_tor_ip(self, ip: str) -> bool:
        # TODO: Implement real check against Tor exit node lists
        return False

    def is_vpn_ip(self, ip: str) -> bool:
        # TODO: Implement real check against VPN databases
        return False
