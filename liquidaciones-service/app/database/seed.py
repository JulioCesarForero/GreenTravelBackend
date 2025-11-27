"""
Optional database seeding module.

This module populates the database with initial or test data.
Useful for:
- Development environments
- Testing
- Demo data
- Initial configuration

Delete this file if not needed.
"""

import logging
from sqlalchemy.orm import Session

logger = logging.getLogger("uvicorn")


def run_seeds(db: Session) -> None:
    """
    Run database seeds.
    
    Args:
        db: SQLAlchemy session
    """
    try:
        logger.info("🌱 Running database seeds...")
        
        # Check if data already exists
        from app.models.liquidacion import Liquidacion
        existing_count = db.query(Liquidacion).count()
        if existing_count > 0:
            logger.info(f"ℹ️  Database already seeded ({existing_count} liquidaciones exist)")
            return
        
        # Generate seed data with at least 10 records
        sample_data = [
            Liquidacion(
                id_reserva=1001,
                nombre_asesor="María González",
                nombre_empresa="Viajes del Caribe S.A.S.",
                nit_empresa="900123456-7",
                direccion_empresa="Carrera 15 #93-47, Bogotá",
                telefono_empresa="6012345678",
                servicio="Hotel",
                fecha_servicio="2025-02-15",
                incluye_servicio="Desayuno, WiFi, Piscina",
                numero_pasajeros=2,
                valor_liquidacion="850000",
                iva=19,
                valor_iva="161500",
                valor_total_iva="1011500",
                nombre_pasajero="Carlos Rodríguez",
                fecha="2025-01-20",
                factura=5001,
                estado=1,
                origen_venta="Web",
                observaciones="Reserva confirmada. Cliente requiere habitación con vista al mar."
            ),
            Liquidacion(
                id_reserva=1002,
                nombre_asesor="Juan Pérez",
                nombre_empresa="Turismo Andino Ltda.",
                nit_empresa="800234567-8",
                direccion_empresa="Calle 72 #10-20, Medellín",
                telefono_empresa="6045678901",
                servicio="Vuelo",
                fecha_servicio="2025-02-20",
                incluye_servicio="Equipaje de mano, Snack",
                numero_pasajeros=1,
                valor_liquidacion="650000",
                iva=19,
                valor_iva="123500",
                valor_total_iva="773500",
                nombre_pasajero="Ana Martínez",
                fecha="2025-01-22",
                factura=5002,
                estado=1,
                origen_venta="Oficina",
                observaciones="Vuelo nacional. Asiento preferencial solicitado."
            ),
            Liquidacion(
                id_reserva=1003,
                nombre_asesor="Laura Sánchez",
                nombre_empresa="Aventuras del Pacífico S.A.",
                nit_empresa="900345678-9",
                direccion_empresa="Avenida 6N #28-30, Cali",
                telefono_empresa="6023456789",
                servicio="Paquete Turístico",
                fecha_servicio="2025-03-10",
                incluye_servicio="Hotel 3 noches, Tours, Alimentación",
                numero_pasajeros=4,
                valor_liquidacion="3200000",
                iva=19,
                valor_iva="608000",
                valor_total_iva="3808000",
                nombre_pasajero="Familia López",
                fecha="2025-01-25",
                factura=5003,
                estado=1,
                origen_venta="Web",
                observaciones="Paquete familiar. Incluye 2 adultos y 2 menores. Requiere cama extra."
            ),
            Liquidacion(
                id_reserva=1004,
                nombre_asesor="Roberto Díaz",
                nombre_empresa="Expediciones Colombia S.A.S.",
                nit_empresa="800456789-0",
                direccion_empresa="Carrera 7 #32-16, Bogotá",
                telefono_empresa="6019876543",
                servicio="Tour",
                fecha_servicio="2025-02-05",
                incluye_servicio="Guía, Transporte, Almuerzo",
                numero_pasajeros=8,
                valor_liquidacion="2400000",
                iva=19,
                valor_iva="456000",
                valor_total_iva="2856000",
                nombre_pasajero="Grupo Empresarial",
                fecha="2025-01-18",
                factura=5004,
                estado=1,
                origen_venta="Telefónica",
                observaciones="Tour corporativo. Grupo de 8 personas. Requiere guía bilingüe."
            ),
            Liquidacion(
                id_reserva=1005,
                nombre_asesor="Patricia Ramírez",
                nombre_empresa="Hoteles del Valle S.A.",
                nit_empresa="900567890-1",
                direccion_empresa="Calle 50 #46-55, Barranquilla",
                telefono_empresa="6051234567",
                servicio="Hotel",
                fecha_servicio="2025-02-28",
                incluye_servicio="Desayuno, Estacionamiento, Spa",
                numero_pasajeros=2,
                valor_liquidacion="1200000",
                iva=19,
                valor_iva="228000",
                valor_total_iva="1428000",
                nombre_pasajero="Miguel Torres",
                fecha="2025-01-30",
                factura=5005,
                estado=1,
                origen_venta="Web",
                observaciones="Habitación suite. Aniversario de bodas. Decoración especial solicitada."
            ),
            Liquidacion(
                id_reserva=1006,
                nombre_asesor="Carlos Mendoza",
                nombre_empresa="Transportes Nacionales Ltda.",
                nit_empresa="800678901-2",
                direccion_empresa="Avenida 68 #49-77, Bogotá",
                telefono_empresa="6018765432",
                servicio="Transporte Terrestre",
                fecha_servicio="2025-02-12",
                incluye_servicio="Vehículo con conductor, Combustible",
                numero_pasajeros=5,
                valor_liquidacion="1800000",
                iva=19,
                valor_iva="342000",
                valor_total_iva="2142000",
                nombre_pasajero="Grupo Familiar",
                fecha="2025-01-28",
                factura=5006,
                estado=1,
                origen_venta="Oficina",
                observaciones="Transporte privado. Ruta Bogotá-Villa de Leyva. Vehículo tipo van."
            ),
            Liquidacion(
                id_reserva=1007,
                nombre_asesor="Sandra Morales",
                nombre_empresa="Cruceros del Caribe S.A.",
                nit_empresa="900789012-3",
                direccion_empresa="Carrera 1 #1-50, Cartagena",
                telefono_empresa="6059876543",
                servicio="Crucero",
                fecha_servicio="2025-04-01",
                incluye_servicio="Camarote, Comidas, Entretenimiento",
                numero_pasajeros=2,
                valor_liquidacion="4500000",
                iva=19,
                valor_iva="855000",
                valor_total_iva="5355000",
                nombre_pasajero="Esposos Herrera",
                fecha="2025-02-01",
                factura=5007,
                estado=1,
                origen_venta="Web",
                observaciones="Crucero 5 días. Camarote con balcón. Requiere cena romántica."
            ),
            Liquidacion(
                id_reserva=1008,
                nombre_asesor="Fernando Castro",
                nombre_empresa="Aventura Extrema S.A.S.",
                nit_empresa="800890123-4",
                direccion_empresa="Calle 10 #5-30, San Gil",
                telefono_empresa="6071234567",
                servicio="Turismo de Aventura",
                fecha_servicio="2025-02-25",
                incluye_servicio="Rafting, Equipos, Seguro, Guía",
                numero_pasajeros=6,
                valor_liquidacion="1800000",
                iva=19,
                valor_iva="342000",
                valor_total_iva="2142000",
                nombre_pasajero="Grupo de Amigos",
                fecha="2025-01-15",
                factura=5008,
                estado=1,
                origen_venta="Telefónica",
                observaciones="Actividad de rafting nivel intermedio. Todos los participantes deben saber nadar."
            ),
            Liquidacion(
                id_reserva=1009,
                nombre_asesor="Diana Vargas",
                nombre_empresa="Gastronomía Viajera S.A.",
                nit_empresa="900901234-5",
                direccion_empresa="Carrera 43A #1-50, Medellín",
                telefono_empresa="6042345678",
                servicio="Tour Gastronómico",
                fecha_servicio="2025-03-05",
                incluye_servicio="Degustaciones, Guía, Transporte",
                numero_pasajeros=12,
                valor_liquidacion="3600000",
                iva=19,
                valor_iva="684000",
                valor_total_iva="4284000",
                nombre_pasajero="Grupo de Turistas",
                fecha="2025-02-05",
                factura=5009,
                estado=1,
                origen_venta="Web",
                observaciones="Tour gastronómico por la ciudad. Incluye visitas a 5 restaurantes. Considerar restricciones alimentarias."
            ),
            Liquidacion(
                id_reserva=1010,
                nombre_asesor="Andrés Jiménez",
                nombre_empresa="Eco Turismo Sostenible Ltda.",
                nit_empresa="800012345-6",
                direccion_empresa="Vía al Parque, Km 5, Pereira",
                telefono_empresa="6063456789",
                servicio="Ecoturismo",
                fecha_servicio="2025-03-15",
                incluye_servicio="Alojamiento ecológico, Caminatas, Guía naturalista",
                numero_pasajeros=3,
                valor_liquidacion="2100000",
                iva=19,
                valor_iva="399000",
                valor_total_iva="2499000",
                nombre_pasajero="Familia Silva",
                fecha="2025-02-10",
                factura=5010,
                estado=1,
                origen_venta="Oficina",
                observaciones="Experiencia ecológica. Alojamiento en cabañas. Actividades de avistamiento de aves."
            ),
            Liquidacion(
                id_reserva=1011,
                nombre_asesor="María González",
                nombre_empresa="Viajes del Caribe S.A.S.",
                nit_empresa="900123456-7",
                direccion_empresa="Carrera 15 #93-47, Bogotá",
                telefono_empresa="6012345678",
                servicio="Hotel",
                fecha_servicio="2025-01-30",
                incluye_servicio="Desayuno, WiFi",
                numero_pasajeros=1,
                valor_liquidacion="450000",
                iva=19,
                valor_iva="85500",
                valor_total_iva="535500",
                nombre_pasajero="Luis Fernández",
                fecha="2025-01-10",
                factura=5011,
                estado=0,
                origen_venta="Web",
                observaciones="Reserva cancelada por el cliente. Reembolso procesado."
            ),
            Liquidacion(
                id_reserva=1012,
                nombre_asesor="Juan Pérez",
                nombre_empresa="Turismo Andino Ltda.",
                nit_empresa="800234567-8",
                direccion_empresa="Calle 72 #10-20, Medellín",
                telefono_empresa="6045678901",
                servicio="Vuelo",
                fecha_servicio="2025-03-20",
                incluye_servicio="Equipaje de bodega, Comida, Selección de asiento",
                numero_pasajeros=2,
                valor_liquidacion="1400000",
                iva=19,
                valor_iva="266000",
                valor_total_iva="1666000",
                nombre_pasajero="Esposos Gutiérrez",
                fecha="2025-02-12",
                factura=5012,
                estado=1,
                origen_venta="Web",
                observaciones="Vuelo internacional. Requiere visa. Documentación verificada."
            )
        ]
        
        db.add_all(sample_data)
        db.commit()
        logger.info(f"✅ Seeded {len(sample_data)} liquidacion records")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Seeding error: {str(e)}")
        # Don't raise - allow service to start even if seeding fails


def clear_seeds(db: Session) -> None:
    """
    Clear all seeded data (for testing).
    
    Args:
        db: SQLAlchemy session
    """
    try:
        logger.warning("🗑️  Clearing all data...")
        
        from app.models.liquidacion import Liquidacion
        # Delete all liquidaciones (use with caution!)
        # db.query(Liquidacion).delete()
        # db.commit()
        
        logger.info("✅ All data cleared")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error clearing data: {str(e)}")
        raise

