# Caso HealthSync: punto de partida

El enunciado completo está en [ENUNCIADO.md](ENUNCIADO.md). Para trabajar este caso, use `CASO=healthsync` en su `.env`.

## Qué trae la plantilla y qué construye el grupo

| Módulo (peso) | Qué trae la plantilla | Qué construye el grupo |
|---|---|---|
| Registro y verificación (20%) | Registro con roles `paciente` (activo de inmediato) y `profesional` (queda `pendiente`). Inicio y cierre de sesión, directorio y perfil de ejemplo. Envío de correo a Mailpit. | Fecha de nacimiento y foto de la tarjeta profesional. Panel de administración para aprobar o rechazar. Referidos y puntos. Bot de validación en C++. |
| Wearables (10%) | Simulador de datos (`/openmhealth/v1/dataPoints`) y cliente HTTP de ejemplo. | Vinculación del dispositivo, importación y almacenamiento de métricas. |
| Consultas virtuales (30%) | — | Directorio, agenda, cobro en créditos, consentimiento, notas clínicas, historial. |
| Alertas programadas (30%) | Robot C++ periódico que consulta `/api/internal/...`. | Umbrales, evaluación periódica, notificaciones al paciente y al profesional. |
| Transferencias (10%) | — | Saldos y transferencias entre usuarios. |

## Cuentas de prueba

Las crea el servicio `seed` con la contraseña `SEED_PASSWORD` del `.env`:

| Rol | Correos |
|---|---|
| admin | valor de `ADMIN_EMAIL` (contraseña `ADMIN_PASSWORD`) |
| paciente | paciente1@healthsync.test, paciente2@healthsync.test |
| profesional | profesional1@healthsync.test, profesional2@healthsync.test |

Si agrega roles, agregue también al menos dos cuentas por rol en `caso.json`.

## API externa simulada

`GET {EXTERNAL_API_BASE_URL}/dataPoints?schema=<métrica>&usuario=<id>&dias=<1-30>`, con el encabezado `Authorization: Bearer <llave>`.

Métricas disponibles: `heart-rate`, `step-count`, `oxygen-saturation`, `sleep-duration`. La serie es determinista por usuario y métrica. Cerca del 5 % de las lecturas salen fuera de rango (por ejemplo 138 bpm o 86 % de oxígeno) para poder probar las alertas.

La respuesta sigue una estructura inspirada en los esquemas de Open mHealth (`header` y `body`), pero no es una réplica exacta. El enunciado menciona la API pública de Open mHealth; Open mHealth publica sobre todo especificaciones de esquemas, y no se verificó que exista un servicio público que entregue datos reales de wearables. Por eso el simulador es la fuente por defecto.
