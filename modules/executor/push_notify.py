def send_push(reminder):
    """
    Sends a push notification for a given reminder.

    Currently a stub — prints to console.
    In production, replace with FCM, Expo, or other push service.

    Args:
        reminder: Reminder object with at least `.text` attribute
    """
    print(f"[PUSH] Reminder: {reminder.text}")
