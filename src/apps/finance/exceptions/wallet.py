class WrongTokenError(Exception):
    """
    Custom exception for invalid token.
    """
    def __init__(self, *args):
        self.message = args[0] if args else None

    def __str__(self):
        if self.message:
            return f"WrongTokenError, {self.message} "
        else:
            return "Invalid token for wallet."


class InsufficientFundsException(Exception):
    """
    Custom exception for insufficient funds in the wallet.
    """
    def __init__(self, *args):
        self.message = args[0] if args else None

    def __str__(self):
        if self.message:
            return f"InsufficientFundsException, {self.message} "
        else:
            return "Insufficient funds in wallet."


class InvalidAmount(Exception):
    """
    Custom exception for invalid amount to charge or to add.
    """
    def __init__(self, *args):
        self.message = args[0] if args else None

    def __str__(self):
        return f"InvalidAmount, {self.message} " if self.message else "Invalid amount."