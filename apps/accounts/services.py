import random
from django.core.cache import cache
from datetime import timedelta

# Constants
OTP_TTL = 300                # 5 minutes
EMAIL_RATE_LIMIT = (3, 600)  # 3 requests per 10 min
IP_RATE_LIMIT = (10, 3600)   # 10 requests per 1 hr
MAX_FAILED_ATTEMPTS = (5, 900)  # 5 attempts per 15 min


class OTPService:
    @staticmethod
    def generate_otp():
        return f"{random.randint(100000, 999999)}"

    @staticmethod
    def get_otp_key(email):
        return f"otp:{email}"

    @staticmethod
    def get_email_counter_key(email):
        return f"otp_email_count:{email}"

    @staticmethod
    def get_ip_counter_key(ip):
        return f"otp_ip_count:{ip}"

    @staticmethod
    def get_failed_attempt_key(email):
        return f"otp_failed:{email}"

    # Rate limiting
    @staticmethod
    def check_email_rate_limit(email):
        key = OTPService.get_email_counter_key(email)
        count = cache.get(key, 0)
        if count >= EMAIL_RATE_LIMIT[0]:
            ttl = cache.ttl(key)
            return False, ttl or EMAIL_RATE_LIMIT[1]
        return True, None

    @staticmethod
    def increment_email_counter(email):
        key = OTPService.get_email_counter_key(email)
        if not cache.get(key):
            cache.set(key, 1, timeout=EMAIL_RATE_LIMIT[1])
        else:
            cache.incr(key)

    @staticmethod
    def check_ip_rate_limit(ip):
        key = OTPService.get_ip_counter_key(ip)
        count = cache.get(key, 0)
        if count >= IP_RATE_LIMIT[0]:
            ttl = cache.ttl(key)
            return False, ttl or IP_RATE_LIMIT[1]
        return True, None

    @staticmethod
    def increment_ip_counter(ip):
        key = OTPService.get_ip_counter_key(ip)
        if not cache.get(key):
            cache.set(key, 1, timeout=IP_RATE_LIMIT[1])
        else:
            cache.incr(key)

    # OTP storage
    @staticmethod
    def store_otp(email, otp):
        cache.set(OTPService.get_otp_key(email), otp, timeout=OTP_TTL)

    @staticmethod
    def get_otp(email):
        return cache.get(OTPService.get_otp_key(email))

    @staticmethod
    def delete_otp(email):
        cache.delete(OTPService.get_otp_key(email))

    # Failed attempts
    @staticmethod
    def check_failed_attempts(email):
        key = OTPService.get_failed_attempt_key(email)
        count = cache.get(key, 0)
        if count >= MAX_FAILED_ATTEMPTS[0]:
            ttl = cache.ttl(key)
            return False, ttl or MAX_FAILED_ATTEMPTS[1]
        return True, None

    @staticmethod
    def increment_failed_attempts(email):
        key = OTPService.get_failed_attempt_key(email)
        if not cache.get(key):
            cache.set(key, 1, timeout=MAX_FAILED_ATTEMPTS[1])
        else:
            cache.incr(key)

    @staticmethod
    def reset_failed_attempts(email):
        cache.delete(OTPService.get_failed_attempt_key(email))
