# utils/net.py
import socket

def is_offline(timeout: float = 1.0) -> bool:
    """
    Checks if the system is offline by attempting to resolve a known host.
    Returns True if no network connection is detected.
    """
    try:
        socket.setdefaulttimeout(timeout)
        # We only check DNS resolution — lightweight and fast
        socket.gethostbyname("1.1.1.1")  # Cloudflare DNS
        return False
    except Exception:
        return True