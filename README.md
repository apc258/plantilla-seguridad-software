<<<<<<< HEAD
# plantilla-seguridad-software
=======
# Plantilla del proyecto: Seguridad en Software

Punto de partida común para los dos casos del curso: **HealthSync** y **AI Agent Marketplace**. Trae la infraestructura base definida en Docker Compose (web, backend, base de datos, robot en C++, correo de pruebas y simulador de la API externa) y ejemplos de uso de cada pieza del stack. Los módulos de negocio de cada caso los construye el grupo.

- Enunciados y punto de partida de cada caso: [`casos/healthsync`](casos/healthsync/README.md) y [`casos/marketplace`](casos/marketplace/README.md).
- Si usted es el **grupo auditor** y recibió el ZIP de otro grupo: lea [`GUIA_AUDITOR.md`](GUIA_AUDITOR.md).

**Todas las piezas del stack deben conservarse en su proyecto**: frontend Vue servido por nginx, backend Flask, MySQL, robot en C++, correo y consumo de la API externa. Puede modificar, reemplazar o extender los ejemplos, pero no eliminar una pieza.

## Arquitectura

```
Navegador ──► localhost:8080 ── web (nginx + SPA Vue) ──/api──► backend (Flask + gunicorn)
                                                                  │      │       │
                                                                 db   mailpit  mock-api
                                                              (MySQL)  (correo) (API externa simulada)
                                                                  ▲
                                               worker (robot C++) ┘ vía /api/internal
```

| Servicio | Tecnología | Función |
|---|---|---|
| `web` | nginx 1.30 + Vue 3 + Bootstrap 5 | Sirve la SPA y redirige `/api` al backend. |
| `backend` | Python 3.13, Flask 3.1, gunicorn | API REST con la lógica de negocio. |
| `seed` | (misma imagen del backend) | Se ejecuta una vez al arrancar y crea el administrador y las cuentas de prueba. |
| `db` | MySQL 8.4 LTS | Base de datos. |
| `worker` | C++17 + libcurl | Robot periódico. Consulta `/api/internal/*` del backend. |
| `mailpit` | Mailpit | Captura todos los correos que envía la aplicación. No envía nada a Internet. |
| `mock-api` | Flask | Simula OpenRouter (marketplace) y datos de wearables tipo Open mHealth (HealthSync). No forma parte de su aplicación: representa un servicio de terceros. |

## Ejemplos incluidos

| Pieza | Ejemplo | Dónde |
|---|---|---|
| Base de datos | Registro, ingreso, directorio con búsqueda, consulta y edición del perfil | `backend/app/rutas_auth.py`, `rutas_generales.py` |
| API externa | Consulta al simulador desde el panel | `backend/app/rutas_generales.py`, `api_externa.py` |
| Correo | Correo de confirmación de registro | `backend/app/correo.py` |
| C++ | Robot que lista las cuentas pendientes de aprobación | `worker/src/robot.cpp`, `backend/app/rutas_internas.py` |
| Vue | Navegación, formularios, directorio, panel | `frontend/src/` |

## Requisitos

- Docker Desktop (Windows o macOS) o Docker Engine con el complemento Compose v2 (Linux).
- Unos 4 GB libres en disco (se descargan imágenes base y librerías).
- Python 3 en la máquina, solo para el script `empaquetar.py`. Si no lo tiene, vea la sección "Sin Python" al final.

Las imágenes se construyen en la máquina de cada persona, así que deberían funcionar tanto en procesadores Intel/AMD como ARM (Apple Silicon).

## Inicio rápido

```bash
# 1. Crear el archivo .env (elija su caso editando CASO)
cp .env.example .env              # Windows PowerShell: Copy-Item .env.example .env

# 2. Construir y levantar todo
docker compose up --build

# 3. Abrir
#    Aplicación:   http://localhost:8080
#    Correos:      http://localhost:8025
```

La cuenta de administrador y la contraseña de las cuentas de prueba están en `.env`. Los correos de las cuentas de prueba de cada caso están en `casos/<caso>/README.md`.

Comandos útiles:

| Para | Comando |
|---|---|
| Ver los logs de un servicio | `docker compose logs -f backend` |
| Reconstruir después de cambiar código | `docker compose up --build` |
| Borrar los datos y empezar de cero | `docker compose down -v` y luego `docker compose up --build` |
| Abrir una consola de MySQL | `docker compose exec db mysql -u root -p app` |

## Estructura

```
.env.example            Variables de entorno
docker-compose.yml      Definición de todos los servicios
ENTREGA.md              Ficha que el grupo diligencia antes de entregar
GUIA_AUDITOR.md         Instrucciones para el grupo que recibe el ZIP
backend/app/
  __init__.py           Fábrica de la app y manejo de errores
  config.py             Configuración desde variables de entorno
  db.py                 Funciones de acceso a la base de datos
  seguridad.py          login_requerido, rol_requerido, usuario_actual
  rutas_auth.py         Registro, ingreso, salida
  rutas_generales.py    Salud, configuración, directorio, perfil, API externa
  rutas_internas.py     Endpoints para el robot
  correo.py             Envío de correo (a Mailpit)
  api_externa.py        Cliente HTTP
  seed.py               Datos semilla
casos/<caso>/           caso.json (roles, cuentas de prueba, API), ENUNCIADO.md, README.md
database/init/          Scripts SQL que se ejecutan al crear la base de datos
frontend/               SPA Vue 3 + configuración de nginx
worker/                 Robot en C++
mock-api/               Simulador de la API externa
scripts/                empaquetar.py
```

## Cómo extender la plantilla

**Tablas nuevas.** Cree `database/init/02-modulos.sql` (se ejecutan en orden alfabético). Esos scripts solo corren cuando el volumen de la base de datos se crea, así que después de cambiarlos ejecute `docker compose down -v`.

**Endpoints nuevos.** Cree un archivo `backend/app/rutas_<modulo>.py` con un `Blueprint` y regístrelo en `__init__.py`.

**Robots.** Agregue endpoints en `rutas_internas.py` y llámelos desde `ejecutar_ciclo()` en `worker/src/robot.cpp`. Si necesita robots con intervalos distintos (cada minuto y cada segundo), duplique el servicio `worker` en `docker-compose.yml` con otro `WORKER_INTERVAL_SECONDS`.

**Vistas.** Agregue componentes en `frontend/src/views/` y rutas en `frontend/src/router/index.js`. Para desarrollar el frontend con recarga en caliente, levante el resto con Docker y ejecute `npm install` y `npm run dev` dentro de `frontend/` (abre en `http://127.0.0.1:5173`).

**Datos semilla.** Agregue en `backend/app/seed.py` los datos que el grupo auditor necesita para probar sus módulos: saldos, agentes, métricas, citas.

## Entrega (fase 1)

1. Diligencie `ENTREGA.md`.
2. Verifique que la aplicación arranca desde cero: `docker compose down -v && docker compose up --build`.
3. Genere el ZIP: `python scripts/empaquetar.py --grupo grupo03`.
4. Suba a la plataforma el ZIP (`entregas/*.zip`) y registre la huella SHA-256 que imprime el script.

El script excluye `.env`, `node_modules`, `dist`, `.git` y los compilados.

## Problemas comunes

- **El puerto 8080, 8025 o 3306 está ocupado.** Cambie el puerto de la izquierda en la sección `ports` del servicio en `docker-compose.yml`.
- **Cambié un `.sql` y no se refleja.** Los scripts de `database/init` solo corren al crear el volumen: `docker compose down -v`.
- **El servicio `seed` falla.** Revise `docker compose logs seed`.

## Sin Python en la máquina

Puede usar el Python de Docker. En Linux, macOS o PowerShell, desde la raíz del proyecto:

```bash
docker run --rm -v "${PWD}:/p" -w /p python:3.13-slim python scripts/empaquetar.py --grupo grupo03
```
>>>>>>> 01824de (primer commit)
