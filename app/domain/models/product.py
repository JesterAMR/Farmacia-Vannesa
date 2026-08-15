from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    # Información Básica
    name: str # Nombre comercial
    generic_name: str
    product_code: str
    description: str
    
    # Inventario
    stock: int
    presentation: str # Ej. Caja, Ampolleta, Frasco
    laboratory: str
    expiration_date: str
    dose: str
    
    # Finanzas
    cost_price: float
    sale_price: float
    
    id: Optional[int] = None

    # Property to interface gracefully with existing code looking for 'price'
    @property
    def price(self) -> float:
        return self.sale_price
