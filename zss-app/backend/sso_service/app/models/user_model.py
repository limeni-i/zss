from enum import Enum
from ..extensions import bcrypt

class Role(Enum):
    """Enum za definisanje korisničkih uloga."""
    PACIJENT = "PACIJENT"
    LEKAR = "LEKAR"
    UCENIK = "UCENIK"
    NASTAVNIK = "NASTAVNIK"
    RODITELJ = "RODITELJ"
    ADMIN = "ADMIN"

class User:
    def __init__(self, name, email, password, role: Role):
        self.name = name
        self.email = email
        self.password = password 
        self.role = role 

    def to_document(self):
        """Pretvara instancu klase u rečnik pogodan za unos u MongoDB."""
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'role': self.role
        }

    @staticmethod
    def hash_password(password):
        """Hešuje lozinku koristeći bcrypt."""
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def check_password(hashed_password, password):
        """Proverava da li se lozinka poklapa sa hešom."""
        return bcrypt.check_password_hash(hashed_password, password)