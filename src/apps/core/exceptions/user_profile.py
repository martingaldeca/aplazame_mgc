class NotCommerceError(Exception):
    """
    Custom exception for invalid token.
    """
    def __init__(self, *args):
        self.message = args[0] if args else None

    def __str__(self):
        if self.message:
            return f"NotCommerceError, {self.message} "
        else:
            return "Only commerce or admin users allowed."
