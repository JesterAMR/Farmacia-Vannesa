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
    
    # Regulación Sanitaria MINSA (Ley 292 / Decreto 19-99)
    sanitary_register: str = "MINSA-REG-2024-001" # Registro Sanitario oficial MINSA (Vigencia 5 años)
    batch_number: str = "LOT-GEN-01"            # Número de lote de fabricación farmacéutica
    is_controlled: bool = False                   # True = Estupefaciente / Psicotrópico (Requiere Receta Médica Retenida)
    
    # Regulación Fiscal DGI (Ley 822 - LCT / Art. 153)
    is_exempt_iva: bool = True                    # True = Exento de IVA (Medicamento humano), False = Gravado con 15% IVA
    
    is_active: bool = True
    id: Optional[int] = None

    # Property to interface gracefully with existing code looking for 'price'
    @property
    def price(self) -> float:
        return self.sale_price
