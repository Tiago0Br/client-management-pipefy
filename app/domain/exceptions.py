class CustomerAlreadyExistsError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Customer with email '{email}' already exists.")

class CustomerNotFoundError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Customer with email '{email}' was not found.")