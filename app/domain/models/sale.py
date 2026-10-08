from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class SaleItem:
    product_id: int
    quantity: int
    price: float  # Precio unitario al momento de la venta
    subtotal: float
    id: Optional[int] = None
    sale_id: Optional[int] = None
    
    # Atributos fiscales y regulatorios
    is_exempt: bool = True               # True = Exento de IVA (Art. 153 Ley 822)
    iva_rate: float = 0.0                # 0.0 o 0.15 (15% DGI)
    iva_amount: float = 0.0              # Monto del IVA calculado para este ítem
    batch_number: Optional[str] = None   # Lote despachado para trazabilidad sanitaria
    product_name: Optional[str] = None

@dataclass
class Sale:
    total: float
    items: List[SaleItem] = field(default_factory=list)
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    client_id: Optional[int] = None
    id: Optional[int] = None
    
    # Desglose Fiscal DGI (Ley 822 - LCT)
    subtotal_exempt: float = 0.0         # Suma de productos exentos de IVA
    subtotal_taxable: float = 0.0        # Suma de productos gravados antes de IVA
    iva_total: float = 0.0               # Impuesto al Valor Agregado total (15%)
    currency: str = "NIO"                # NIO (Córdobas) o USD (Dólares)
    exchange_rate: float = 36.62         # Tipo de cambio oficial BCN (NIO por 1 USD)
    total_usd: float = 0.0               # Total equivalente en Dólares
    
    # Regulación Sanitaria para Fármacos Controlados (Ley 292 / Psicotrópicos)
    prescription_doctor: Optional[str] = None   # Nombre del Médico Colegiado
    doctor_minsa_code: Optional[str] = None     # Código MINSA del Médico
    prescription_number: Optional[str] = None   # Número de folio de la receta retenida
    
    # Facturación Electrónica DGI
    fiscal_xml: Optional[str] = None            # XML de Factura Electrónica normalizado
    dgi_auth_number: Optional[str] = None       # Número de Autorización Fiscal / Serie DGI
