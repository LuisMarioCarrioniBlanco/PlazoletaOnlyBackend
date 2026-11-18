# Backend Plazoleta de Comidas

Backend Java para las 18 historias del reto Plazoleta, organizado en dos microservicios Spring Boot con arquitectura hexagonal. La base de datos H2 funciona en modo archivo y conserva los registros al cerrar los servicios.

## Requisitos

- JDK 21
- Maven 3.9 o superior

## Iniciar el backend

Abre dos terminales en la carpeta del proyecto.

Terminal 1:

```powershell
cd usuarios-service
mvn spring-boot:run
```

Terminal 2:

```powershell
cd plazoleta-service
mvn spring-boot:run
```

La primera ejecución descarga las dependencias Maven. Al iniciar, cada servicio crea su carpeta `data` y su base de datos local. No borres esas carpetas si quieres conservar los datos.

## Swagger

- Usuarios: http://localhost:8081/swagger-ui.html
- Plazoleta: http://localhost:8082/swagger-ui.html
- OpenAPI: http://localhost:8081/v3/api-docs y http://localhost:8082/v3/api-docs

El administrador inicial es `admin@plazoleta.local` con clave `Admin123!`. Cámbialos con `INITIAL_ADMIN_EMAIL` y `INITIAL_ADMIN_PASSWORD` antes de iniciar si necesitas otros valores. Las operaciones protegidas usan JWT. En Swagger pulsa **Authorize** e ingresa el token del login.

## Historias disponibles

| HU | Funcionalidad |
|---|---|
| HU1–HU8 | Usuarios, autenticación, restaurantes, platos, empleados y clientes |
| HU9 | Listar restaurantes con paginación |
| HU10 | Listar menú activo, con filtro de categoría y paginación |
| HU11 | Crear pedido con platos de un restaurante y cantidades |
| HU12 | Bandeja de pedidos del empleado filtrada por estado y paginada |
| HU13 | Asignar pedido al empleado e iniciar preparación |
| HU14 | Marcar pedido listo y generar PIN de recogida |
| HU15 | Entregar pedido con validación del PIN |
| HU16 | Cancelar pedido propio mientras siga pendiente |
| HU17 | Consultar la trazabilidad de un pedido propio |
| HU18 | Consultar duración por pedido y ranking de empleados del restaurante propio |

El flujo de pedidos está descrito paso a paso en [docs/guia-presentacion-HU1-HU18.md](docs/guia-presentacion-HU1-HU18.md).

## Nota sobre SMS

El proyecto no tiene credenciales de Twilio ni de otro proveedor. Para que el flujo se pueda demostrar localmente, al marcar un pedido como listo genera un PIN, lo devuelve una sola vez en esa respuesta de Swagger y registra el aviso simulado en la consola. El PIN luego se exige para entregar el pedido. Un SMS real requiere configurar un proveedor y sus credenciales.

## Datos locales

Las bases quedan en `usuarios-service/data/usuarios.mv.db` y `plazoleta-service/data/plazoleta.mv.db`. H2 corre embebida dentro de cada servicio; no hay servidor de base de datos que instalar. El archivo de base de datos queda fuera de Git. La configuración se puede cambiar con las variables `DB_URL`, `DB_USERNAME` y `DB_PASSWORD`.
