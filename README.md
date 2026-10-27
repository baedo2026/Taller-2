# Taller Evaluado II — Backend con FastAPI, PostgreSQL y Docker

API CRUD de estudiantes y mascotas. La actividad reemplaza el almacenamiento en memoria por persistencia SQLAlchemy, migraciones Alembic y servicios levantados con Docker Compose.

## Requisitos

- Docker Desktop iniciado con el backend WSL 2.
- Git para trabajar en una rama por integrante y enviar un Pull Request.
- Para desarrollo local fuera de Docker: Python 3.13 y uv.

## Iniciar el proyecto con Docker Desktop

Abre PowerShell en la carpeta del repositorio. Crea tu archivo local de configuración una sola vez y levanta los servicios:

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose up --build -d
docker compose ps
```

La primera construcción descarga imágenes e instala dependencias. El servicio `api` espera a que PostgreSQL esté saludable, ejecuta `alembic upgrade head` y luego inicia FastAPI.

| Servicio | Dirección |
| --- | --- |
| Aplicación web | http://localhost:3000 |
| Documentación interactiva | http://localhost:3000/docs |
| Adminer | http://localhost:8080 |
| PostgreSQL desde Windows | localhost:5432 |

En Adminer selecciona sistema **PostgreSQL**, servidor `db`, usuario `taller_user`, contraseña `taller_password` y base `taller_backend` (o los valores que pusiste en `.env`). Dentro de la red de Compose, la API y Adminer usan el nombre de servicio `db`; desde Windows se usa `localhost`.

Para ver los registros de la API: `docker compose logs -f api`. Para detener los contenedores sin borrar la base: `docker compose down`. El volumen `postgres_data` mantiene los datos. `docker compose down -v` también borra ese volumen y toda la información guardada.

## Variables de entorno

Copia `.env.example` como `.env` y cambia los valores si necesitas otros puertos o credenciales. Compose usa estas variables para la base, Adminer y los puertos publicados. `.env` está excluido de Git; comparte solo `.env.example`, nunca contraseñas personales.

La cadena de conexión de la API en Docker apunta a `db:5432`. La de `.env.example` apunta a `localhost:5432` para poder ejecutar la API directamente desde Windows.

## Persistencia y migraciones

Los modelos SQLAlchemy están en `app/db/models.py` y los repositorios consultan PostgreSQL mediante una sesión por petición. Alembic versiona el esquema en `alembic/versions/`; la migración inicial crea `students`, `pets`, las claves únicas y la relación de mascota con estudiante con borrado en cascada.

Para preparar una nueva revisión después de cambiar modelos, con la base disponible:

```powershell
uv run alembic revision --autogenerate -m "describe el cambio"
```

Revisa el archivo generado y luego aplica las migraciones con `uv run alembic upgrade head`. El contenedor de la API aplica automáticamente las pendientes al iniciar.

## Transacción y comprobación de rollback

`POST /api/students` puede crear al estudiante y varias mascotas en una sola solicitud. El servicio ejecuta esas escrituras dentro de `Session.begin()`. Si una falla, la transacción revierte todas las inserciones. También hay restricciones únicas en PostgreSQL para evitar duplicados incluso ante solicitudes concurrentes.

Comprueba el rollback desde `http://localhost:3000/docs`:

1. Ejecuta `GET /api/students` y anota el total actual.
2. Ejecuta `POST /api/students` con un correo y usuario que no existan, y dos mascotas con el mismo nombre:

```json
{
  "name": "Prueba Rollback",
  "username": "prueba_rollback",
  "email": "rollback@example.com",
  "age": 21,
  "pets": [
    { "name": "Michi", "species": "gato", "age": 2 },
    { "name": "Michi", "species": "gato", "age": 3 }
  ]
}
```

3. La API debe responder `409 Conflict` por el nombre duplicado.
4. Vuelve a ejecutar `GET /api/students`: el total debe ser el mismo y `prueba_rollback` no debe aparecer. Así se comprueba que ni el estudiante ni la primera mascota quedaron guardados.

## Endpoints

| Método | Ruta | Operación |
| --- | --- | --- |
| GET | `/api/students` | Listar estudiantes |
| POST | `/api/students` | Crear estudiante; acepta `pets` opcional |
| GET | `/api/students/{studentId}` | Obtener estudiante |
| PATCH | `/api/students/{studentId}` | Actualizar estudiante |
| DELETE | `/api/students/{studentId}` | Eliminar estudiante y sus mascotas |
| GET | `/api/students/{studentId}/pets` | Listar mascotas |
| POST | `/api/students/{studentId}/pets` | Crear mascota |
| PATCH | `/api/students/{studentId}/pets/{petId}` | Actualizar mascota |
| DELETE | `/api/students/{studentId}/pets/{petId}` | Eliminar mascota |

La respuesta conserva el envelope existente (`code`, `success`, `message`, `data` y, en errores, `errors`). Pydantic valida los datos; email y username de estudiantes son únicos, y el nombre de mascota es único por estudiante.

## Ejecutar solo la API desde Windows (opcional)

Usa este modo si tienes PostgreSQL levantado y quieres recargar FastAPI al editar. Asegúrate de que `DATABASE_URL` en `.env` use `localhost`:

```powershell
uv sync
docker compose up -d db
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

## Trabajo en Git

Cada integrante debe desarrollar en su propia rama, subir sus cambios y abrir un Pull Request hacia `main`. No se debe trabajar directamente sobre `main`. La pauta solicita al menos un PR fusionado por integrante; el equipo debe revisar y fusionar los PRs.

```powershell
git switch -c nombre-de-tu-rama
git add .
git commit -m "Implementa persistencia y Docker Compose"
git push -u origin nombre-de-tu-rama
```

Luego abre el repositorio en GitHub y crea un Pull Request de tu rama hacia `main`.