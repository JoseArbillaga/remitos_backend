"""
Configuración de Celery para procesamiento asíncrono
"""
from celery import Celery
from config import settings

# Crear instancia de Celery
celery_app = Celery(
    "remitos_backend",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=[
        "app.tasks.afip_tasks",
        "app.tasks.remito_tasks"
    ]
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Argentina/Buenos_Aires",
    enable_utc=True,
    
    # Configuración de reintentos
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Configuración de resultados
    result_expires=3600,  # 1 hora
    
    # Configuración de tareas
    task_routes={
        "app.tasks.afip_tasks.enviar_remito_afip_async": {"queue": "afip_queue"},
        "app.tasks.afip_tasks.enviar_lote_remitos_afip": {"queue": "afip_batch_queue"},
        "app.tasks.remito_tasks.generar_reporte_remitos": {"queue": "reports_queue"},
    },
    
    # Límites de velocidad
    task_annotations={
        "app.tasks.afip_tasks.enviar_remito_afip_async": {"rate_limit": "10/m"},
        "app.tasks.afip_tasks.enviar_lote_remitos_afip": {"rate_limit": "2/m"},
    }
)