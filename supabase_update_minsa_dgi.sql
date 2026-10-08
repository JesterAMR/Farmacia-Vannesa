-- ====================================================================
-- MIGRACIÓN SQL SUPABASE: ACTUALIZACIÓN NORMATIVA MINSA Y FISCAL DGI
-- Proyecto: Farmacia Vannesa
-- ====================================================================
-- Instrucciones:
-- 1. Abre tu panel de Supabase: https://supabase.com/dashboard
-- 2. Entra a tu proyecto -> SQL Editor -> New Query.
-- 3. Pega este contenido y presiona "RUN".
-- ====================================================================

-- 1. Actualización de tabla PRODUCTS (Medicamentos y Productos)
ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS sanitary_register VARCHAR(100) DEFAULT 'REG-MINSA-PENDIENTE',
ADD COLUMN IF NOT EXISTS batch_number VARCHAR(100) DEFAULT 'LOTE-DEFAULT',
ADD COLUMN IF NOT EXISTS is_controlled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_exempt_iva BOOLEAN DEFAULT TRUE;

-- 2. Actualización de tabla SALES (Ventas y Facturación Fiscal)
ALTER TABLE public.sales 
ADD COLUMN IF NOT EXISTS subtotal_exempt NUMERIC(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS subtotal_taxable NUMERIC(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS iva_total NUMERIC(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'NIO',
ADD COLUMN IF NOT EXISTS exchange_rate NUMERIC(12, 4) DEFAULT 36.6200,
ADD COLUMN IF NOT EXISTS total_usd NUMERIC(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS prescription_doctor VARCHAR(150) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS doctor_minsa_code VARCHAR(50) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS prescription_number VARCHAR(50) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS fiscal_xml TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS dgi_auth_number VARCHAR(100) DEFAULT NULL;

-- 3. Restricciones de Calidad e Integridad de Datos (Auditoría)
DO $$
BEGIN
    -- Validar precios mayores a 0 y costo no negativo
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_product_prices_positive') THEN
        ALTER TABLE public.products ADD CONSTRAINT check_product_prices_positive CHECK (sale_price > 0 AND cost_price >= 0);
    END IF;

    -- Validar stock no negativo
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_product_stock_non_negative') THEN
        ALTER TABLE public.products ADD CONSTRAINT check_product_stock_non_negative CHECK (stock >= 0);
    END IF;

    -- Validar longitud de cédula / RUC de clientes
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_client_identity_card_len') THEN
        ALTER TABLE public.clients ADD CONSTRAINT check_client_identity_card_len CHECK (length(identity_card) >= 3);
    END IF;
END $$;

-- 4. Notificación de éxito
SELECT 'Migración MINSA/DGI y Calidad de Datos completada con éxito en Supabase' AS status;
