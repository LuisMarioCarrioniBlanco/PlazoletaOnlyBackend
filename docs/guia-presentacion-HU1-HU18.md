# Guía de presentación del backend Plazoleta

Esta guía ayuda a demostrar las historias HU1–HU18 desde Swagger. Abre Usuarios en `http://localhost:8081/swagger-ui.html` y Plazoleta en `http://localhost:8082/swagger-ui.html`. Inicia sesión con el administrador, copia el JWT y autorízalo en cada Swagger donde se indique. La autorización se configura por separado en cada servicio.

## Preparación

1. Inicia `usuarios-service` y `plazoleta-service` en terminales separadas con `mvn spring-boot:run`.
2. Inicia sesión en Usuarios con `admin@plazoleta.local` y `Admin123!` en `POST /api/v1/auth/login`.
3. En Swagger de Usuarios y Plazoleta pulsa **Authorize** y pega el JWT. Repite la autorización cada vez que cambies de usuario.
4. Guarda los IDs que devuelve la API: `propietarioId`, `restauranteId`, `platoId`, `clienteId`, `empleadoId` y `pedidoId`.

El administrador inicial puede tener otra clave si se configuró por variables de entorno. No incluyas JWT completos en capturas.

## Flujo recomendado para demostrar HU1–HU9

| HU | Operación en Swagger | Evidencia a mostrar |
|---|---|---|
| 1 | Usuarios `POST /api/v1/usuarios/propietarios` | El rol queda como `PROPIETARIO`; un menor de edad se rechaza. Usa token administrador. |
| 2 | Plazoleta `POST /api/v1/restaurantes` | Restaurante con NIT y `propietarioId`; token administrador. |
| 3 | Plazoleta `POST /api/v1/restaurantes/{restauranteId}/platos` | Plato asociado al restaurante y `activo: true`; token del propietario. |
| 4 | Plazoleta `PATCH /api/v1/restaurantes/{restauranteId}/platos/{platoId}` | Cambian precio o descripción; los demás campos se conservan. |
| 5 | Usuarios `POST /api/v1/auth/login` | Login con clave válida da JWT; clave errónea da 401 y el rol controla acceso. |
| 6 | Plazoleta `POST /api/v1/restaurantes/{restauranteId}/empleados` | Empleado queda asociado al restaurante; luego muestra su login. Token propietario. |
| 7 | Plazoleta `PATCH /api/v1/restaurantes/{restauranteId}/platos/{platoId}/estado` | Cambia `activo` entre `false` y `true`; token propietario. |
| 8 | Usuarios `POST /api/v1/usuarios/clientes` | Cuenta con rol `CLIENTE`; inicia sesión con ella. |
| 9 | Plazoleta `GET /api/v1/restaurantes?page=0&size=10` | Orden alfabético y metadatos de paginación; token cliente. |

Para HU1, HU2, HU3, HU6 y HU8 usa datos nuevos en cada ejecución: correo, documento y NIT deben ser únicos.

## Flujo de pedidos HU10–HU18

Usa el mismo restaurante, un plato activo, el cliente y el empleado creados antes. Para probar nuevamente HU11, termina o cancela el pedido activo previo.

### HU10: consultar el menú

Con JWT de cliente en Plazoleta, ejecuta `GET /api/v1/restaurantes/{restauranteId}/platos?page=0&size=10`. Para filtrar añade `&categoria=Platos%20fuertes`. La respuesta solo incluye platos activos y trae datos de paginación.

### HU11: crear un pedido

Con JWT de cliente ejecuta `POST /api/v1/pedidos`:

```json
{
  "restauranteId": 1,
  "platos": [
    { "platoId": 1, "cantidad": 2 }
  ]
}
```

Reemplaza los IDs por los tuyos. La respuesta debe tener estado `PENDIENTE`. Para un mismo cliente solo puede haber un pedido activo en `PENDIENTE`, `EN_PREPARACION` o `LISTO`.

### HU12: bandeja de pedidos del empleado

Con JWT de empleado ejecuta `GET /api/v1/pedidos?estado=PENDIENTE&page=0&size=10`. Prueba también sin `estado`. Solo aparecen pedidos del restaurante asociado al empleado.

### HU13: asignarse e iniciar la preparación

Con el JWT del empleado asignado ejecuta `PATCH /api/v1/pedidos/{pedidoId}/preparacion`. El pedido cambia a `EN_PREPARACION` y queda asociado al ID del empleado.

### HU14: marcar pedido listo

Con el mismo JWT ejecuta `PATCH /api/v1/pedidos/{pedidoId}/listo`. La respuesta entrega el PIN de seis dígitos; cópialo para HU15. El backend deja un mensaje `[AVISO SMS LOCAL]` en la consola. Es una simulación local porque el proyecto no tiene credenciales de proveedor SMS.

### HU15: entregar el pedido

Con JWT de empleado ejecuta `PATCH /api/v1/pedidos/{pedidoId}/entregar`:

```json
{ "pinSeguridad": "123456" }
```

Reemplaza el PIN por el recibido en HU14. Un PIN incorrecto se rechaza; solo un pedido `LISTO` puede pasar a `ENTREGADO`.

### HU16: cancelar pedido pendiente

Con JWT del cliente dueño del pedido ejecuta `PATCH /api/v1/pedidos/{pedidoId}/cancelar`. La cancelación solo funciona en `PENDIENTE`. Para demostrar el rechazo, intenta cancelar después de iniciar preparación.

### HU17: consultar trazabilidad

Con JWT del cliente ejecuta `GET /api/v1/pedidos/{pedidoId}/trazabilidad`. Muestra los estados y fechas del pedido. Otro cliente no puede consultar ese historial.

### HU18: consultar eficiencia

Con JWT del propietario ejecuta `GET /api/v1/restaurantes/{restauranteId}/eficiencia`. Muestra la duración de pedidos entregados y el ranking ascendente de duración promedio por empleado. Completa al menos un pedido con HU11–HU15 para que haya datos.

## Respuestas de error útiles para la demostración

- `401`: falta un JWT válido o las credenciales de login no son correctas.
- `403`: el JWT pertenece a un rol que no puede usar esa operación.
- `400`: se incumple una regla, por ejemplo precio, estado, PIN, pedido activo o paginación inválidos.
- `404`: el recurso no existe o pertenece a otro usuario/restaurante.
- `409`: ya existe una cuenta con ese correo/documento o un restaurante con ese NIT.

Los datos quedan guardados en las bases H2 bajo las carpetas `data` de cada microservicio. Detener y volver a iniciar los servicios no borra el contenido.
