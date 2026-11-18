from docx import Document
from docx.shared import Inches, Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path
import hashlib
ref=Path(r'C:\Users\Luis Mario\Downloads\Guia-pruebas-Plazoleta-HU1-HU9-para-copiar.docx')
assert hashlib.sha256(ref.read_bytes()).hexdigest()=='ff5b9a6d068f1f04c3590f7563496e342a0e204ab4210ab2101ead4581de4051'
out=Path(r'docs\\Guia-pruebas-Plazoleta-HU1-HU18.docx')
d=Document(str(ref)); body=d._element.body
for child in list(body):
 if child.tag != qn('w:sectPr'): body.remove(child)
# The retained document's custom styles and section settings remain the layout authority.
def sty(name):
 ids={'First Paragraph':'FirstParagraph','Compact':'Compact','Source Code':'SourceCode','Body Text':'BodyText'}
 return d.styles.get_by_id(ids.get(name,name.replace(' ','') ),1)
def p(text='',style='First Paragraph',bold_prefix=None):
 x=d.add_paragraph(style=sty(style))
 if bold_prefix and text.startswith(bold_prefix):
  x.add_run(bold_prefix).bold=True;x.add_run(text[len(bold_prefix):])
 else:x.add_run(text)
 return x
def labelblock(items):
 return '\n'.join(f'{k}: {v}' for k,v in items)
def code(text):
 x=d.add_paragraph(style=sty('Source Code'));x.add_run(text);return x
def compact(text):return p(text,'Compact')
def bodytext(text,bold_prefix=None):return p(text,'Body Text',bold_prefix)
def heading(text,level=2):return d.add_paragraph(text,style=d.styles.get_by_id(f'Heading{level}',1))

heading('Guía de pruebas del backend — Plazoleta de comidas (HU1–HU18)',1)
p('Objetivo: probar, en orden, las dieciocho historias de usuario del backend usando Swagger y los dos microservicios locales. En cada historia se indican el endpoint, el rol, los datos, el resultado esperado y una prueba negativa para comprobar la regla principal.')
heading('1. Antes de empezar',2)
p('Debes tener ejecutándose los dos microservicios. Las bases locales son H2 en modo archivo; no necesitas instalar ni iniciar MySQL. Swagger está disponible en:')
compact('Usuarios / Swagger: http://localhost:8081/swagger-ui.html')
compact('Plazoleta / Swagger: http://localhost:8082/swagger-ui.html')
p('Si necesitas iniciar los servicios, abre dos terminales desde la raíz del proyecto y ejecuta:')
code('# Terminal 1\ncd usuarios-service\nmvn spring-boot:run')
code('# Terminal 2\ncd plazoleta-service\nmvn spring-boot:run')
heading('Cómo ejecutar cada petición en Swagger',3)
for t in ['Abre el Swagger del microservicio indicado en la historia.','Expande el endpoint y pulsa Try it out.','Pega el JSON indicado en Request body cuando la operación lo requiera. Sustituye los marcadores entre llaves por los IDs reales que devolvió tu API.','Pulsa Execute y revisa el código HTTP y el cuerpo de la respuesta.','Para las rutas protegidas, pulsa Authorize e introduce el token del usuario con el rol indicado. Cada Swagger conserva su autorización por separado.','No compartas capturas que muestren el JWT completo ni claves.']:
 compact(t)
heading('Cuentas e IDs que debes tener a mano',3)
p('El administrador inicial es admin@plazoleta.local con clave Admin123!, a menos que se hayan configurado INITIAL_ADMIN_EMAIL e INITIAL_ADMIN_PASSWORD. Al crear los recursos, registra sus IDs:')
t=d.add_table(rows=1,cols=2);t.alignment=WD_TABLE_ALIGNMENT.CENTER
for i,v in enumerate(['Dato','Valor que debes anotar']):
 c=t.rows[0].cells[i];c.text=v;sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'D9EAF7');c._tc.get_or_add_tcPr().append(sh)
 for r in c.paragraphs[0].runs:r.bold=True
for a,b in [('propietarioId','ID devuelto por HU1'),('restauranteId','ID devuelto por HU2'),('platoId','ID devuelto por HU3'),('empleadoId','ID devuelto por HU6'),('clienteId','ID devuelto por HU8'),('pedidoId','ID devuelto por HU11')]:
 cells=t.add_row().cells;cells[0].text=a;cells[1].text=b
p('Usa correo, documento y NIT nuevos cada vez que crees un registro. Los datos quedan en las bases H2 de las carpetas data de cada servicio, así que detener el servicio no elimina las pruebas anteriores.')
heading('2. Preparación: iniciar sesión y obtener JWT',2)
p('Las rutas de login son públicas. Usa POST /api/v1/auth/login en Usuarios; el token se debe autorizar por separado en Usuarios y en Plazoleta.')
heading('2.1 Iniciar sesión como administrador',3)
p(labelblock([('Microservicio','Usuarios'),('Endpoint','POST /api/v1/auth/login'),('Autorización','Pública'),('Esperado','200 OK; devuelve token, tipo, id, correo y rol ADMINISTRADOR.')]))
code('{\n  "correo": "admin@plazoleta.local",\n  "clave": "Admin123!"\n}')
p('Copia el token para las pruebas de HU1 y HU2. Si la clave inicial fue cambiada, utiliza la configurada para tu entorno.')
heading('2.2 Prueba negativa de login',3)
p('Repite el login con una clave incorrecta. Esperado: 401 Unauthorized. No uses ese token para las pruebas siguientes.')
code('{\n  "correo": "admin@plazoleta.local",\n  "clave": "ClaveIncorrecta123!"\n}')

stories=[
('3. HU1 — Crear propietario',[('Microservicio','Usuarios'),('Endpoint','POST /api/v1/usuarios/propietarios'),('Rol requerido','ADMINISTRADOR'),('Esperado','201 Created; la respuesta identifica un usuario con rol PROPIETARIO.')],
'Autoriza el token administrador. Envía datos nuevos para crear un propietario adulto. La clave no debe aparecer en la respuesta.',
'{\n  "nombre": "Laura",\n  "apellido": "Prueba",\n  "documentoIdentidad": "1034567891",\n  "celular": "+573001234568",\n  "fechaNacimiento": "1998-04-10",\n  "correo": "laura.propietaria@example.com",\n  "clave": "ClaveLaura123!"\n}',
'Comprueba que la respuesta tenga un ID y rol PROPIETARIO. Guarda el ID como propietarioId. La clave no debe devolverse.',
'Prueba fecha de nacimiento para una persona menor de 18 años, documento no numérico o correo/documento ya registrado. Cada solicitud debe rechazarse.'),
('4. HU2 — Crear restaurante',[('Microservicio','Plazoleta'),('Endpoint','POST /api/v1/restaurantes'),('Rol requerido','ADMINISTRADOR'),('Esperado','201 Created; devuelve el restaurante con propietarioId.')],
'Autoriza el token administrador en Swagger de Plazoleta. Usa el propietarioId obtenido en HU1. Plazoleta consulta Usuarios para validar que exista y tenga rol PROPIETARIO.',
'{\n  "nombre": "Restaurante de Prueba",\n  "nit": "900123457",\n  "direccion": "Calle 20 # 15-30",\n  "telefono": "+573001234569",\n  "urlLogo": "https://example.com/logo-prueba.png",\n  "propietarioId": 1\n}',
'Reemplaza propietarioId por el ID real. Comprueba que la respuesta devuelva id y propietarioId correctos. Anota id como restauranteId.',
'Prueba NIT duplicado o no numérico, nombre formado solo por números y propietarioId inexistente o de un usuario que no sea PROPIETARIO. También intenta la operación sin rol administrador.'),
('5. HU3 — Crear plato',[('Microservicio','Plazoleta'),('Endpoint','POST /api/v1/restaurantes/{restauranteId}/platos'),('Rol requerido','PROPIETARIO dueño del restaurante'),('Esperado','201 Created; plato asociado al restaurante y activo=true.')],
'Inicia sesión como propietario por POST /api/v1/auth/login y autoriza el token en Plazoleta. En la ruta usa restauranteId real.',
'{\n  "nombre": "Arroz con coco",\n  "precio": 18000,\n  "descripcion": "Arroz con coco acompañado de pescado",\n  "urlImagen": "https://example.com/arroz-coco.png",\n  "categoria": "Platos fuertes"\n}',
'Comprueba que la respuesta incluya id, restauranteId correcto y activo=true. Guarda id como platoId.',
'Prueba precio cero o negativo, campos requeridos vacíos, restaurante inexistente y token de un propietario que no sea dueño.'),
('6. HU4 — Modificar plato',[('Microservicio','Plazoleta'),('Endpoint','PATCH /api/v1/restaurantes/{restauranteId}/platos/{platoId}'),('Rol requerido','PROPIETARIO dueño del restaurante'),('Esperado','200 OK; solo cambian precio y descripción.')],
'Usa los IDs reales de HU2 y HU3 y autoriza al propietario. El cuerpo admite únicamente los campos que esta historia permite modificar.',
'{\n  "precio": 20000,\n  "descripcion": "Arroz con coco, pescado y ensalada"\n}',
'Comprueba que precio/descripción cambiaron y que nombre, URL de imagen, categoría, estado y restaurante se conservaron. También puedes enviar solo precio o solo descripción.',
'Prueba cuerpo vacío, precio no positivo, plato de otro restaurante o token de un propietario diferente.'),
('7. HU5 — Autenticación y permisos por rol',[('Microservicio','Usuarios para login; ambos servicios para autorización'),('Endpoint','POST /api/v1/auth/login y operaciones protegidas'),('Roles','ADMINISTRADOR, PROPIETARIO, EMPLEADO y CLIENTE'),('Esperado','Login válido devuelve 200 y JWT; cada rol solo accede a sus operaciones.')],
'Inicia sesión por separado como administrador, propietario, empleado (después de HU6) y cliente (después de HU8). Para cada cuenta, revisa el rol devuelto. Autoriza cada token en el Swagger donde probarás su permiso.',
'',
'Como pruebas de permiso, usa administrador para HU1/HU2, propietario para crear platos/empleados, empleado para la bandeja y cliente para consultar restaurantes o crear pedidos. El JWT emitido por Usuarios debe ser reconocido por Plazoleta.',
'Login con clave incorrecta debe responder 401. Token válido con rol que no corresponda debe recibir rechazo de autorización (403). Token ausente o inválido también debe ser rechazado.'),
('8. HU6 — Crear empleado',[('Microservicio','Plazoleta crea la solicitud; Usuarios guarda la cuenta'),('Endpoint','POST /api/v1/restaurantes/{restauranteId}/empleados'),('Rol requerido','PROPIETARIO del restaurante'),('Esperado','201 Created; rol EMPLEADO y restauranteId asociado.')],
'Autoriza el token propietario en Plazoleta y utiliza el restauranteId correspondiente. La integración interna con Usuarios se realiza desde el backend y requiere X-Internal-Token.',
'{\n  "nombre": "Carlos",\n  "apellido": "Empleado",\n  "documentoIdentidad": "1034567892",\n  "celular": "+573001234570",\n  "correo": "carlos.empleado@example.com",\n  "clave": "ClaveCarlos123!"\n}',
'Comprueba id, rol EMPLEADO y restauranteId en la respuesta; guarda empleadoId. Luego ejecuta login en Usuarios con correo/clave del empleado y confirma su rol.',
'Prueba correo/documento repetidos, token de cliente o administrador y propietario que no sea dueño del restaurante.'),
('9. HU7 — Habilitar o deshabilitar plato',[('Microservicio','Plazoleta'),('Endpoint','PATCH /api/v1/restaurantes/{restauranteId}/platos/{platoId}/estado'),('Rol requerido','PROPIETARIO del restaurante'),('Esperado','200 OK; cambia activo del plato propio.')],
'Autoriza al propietario y sustituye ambos IDs por valores reales.',
'{\n  "activo": false\n}',
'Comprueba activo=false. Repite el mismo endpoint con activo=true y confirma la reactivación. Después usa HU10 para mostrar que el plato inactivo desaparece del menú.',
'Un propietario de otro restaurante no debe poder cambiar el estado del plato.'),
('10. HU8 — Crear cuenta de cliente',[('Microservicio','Usuarios'),('Endpoint','POST /api/v1/usuarios/clientes'),('Autorización','Pública; no necesita token'),('Esperado','201 Created; rol CLIENTE.')],
'Envía datos nuevos. El rol es fijo CLIENTE y no se selecciona en el cuerpo.',
'{\n  "nombre": "Sofia",\n  "apellido": "Cliente",\n  "documentoIdentidad": "1034567893",\n  "celular": "+573001234571",\n  "correo": "sofia.cliente@example.com",\n  "clave": "ClaveSofia123!"\n}',
'Comprueba ID y rol CLIENTE, sin que la respuesta muestre la clave. Guarda clienteId. Inicia sesión y conserva su token para HU9–HU11, HU16 y HU17.',
'Prueba correo/documento duplicados y datos requeridos inválidos.'),
('11. HU9 — Listar restaurantes',[('Microservicio','Plazoleta'),('Endpoint','GET /api/v1/restaurantes?page=0&size=10'),('Rol requerido','CLIENTE'),('Esperado','200 OK; orden alfabético y metadatos de paginación.')],
'Autoriza el token cliente de HU8 en Swagger de Plazoleta. No hay cuerpo JSON.',
'',
'Comprueba orden ascendente por nombre, que cada elemento incluya nombre y urlLogo, y que la respuesta incluya page, size, totalElements y totalPages. Prueba también size=1 en páginas consecutivas.',
'Usa token de administrador/propietario, page negativa, size=0 y size mayor que 100; deben rechazarse.'),
('12. HU10 — Consultar menú activo',[('Microservicio','Plazoleta'),('Endpoint','GET /api/v1/restaurantes/{restauranteId}/platos?page=0&size=10'),('Rol requerido','CLIENTE'),('Esperado','200 OK; solo platos activos, paginados y filtrables por categoría.')],
'Autoriza cliente y usa restauranteId real. No hay cuerpo JSON.',
'',
'Comprueba que el plato activo de HU3 aparezca con sus datos. Prueba el filtro agregando &categoria=Platos%20fuertes (usa la categoría real) y confirma que solo devuelve esa categoría. Desactiva el plato con HU7 y repite para demostrar que ya no aparece.',
'Prueba categoría sin coincidencias, restaurante inexistente y parámetros de paginación inválidos.'),
('13. HU11 — Crear pedido',[('Microservicio','Plazoleta'),('Endpoint','POST /api/v1/pedidos'),('Rol requerido','CLIENTE'),('Esperado','201 Created; estado inicial PENDIENTE.')],
'Autoriza al cliente de HU8. Usa el mismo restaurante y un plato activo del menú.',
'{\n  "restauranteId": 1,\n  "platos": [\n    { "platoId": 1, "cantidad": 2 }\n  ]\n}',
'Reemplaza los IDs por los reales. Comprueba clienteId, restauranteId, detalle/cantidad y estado PENDIENTE. Guarda pedidoId.',
'Prueba cantidad cero, lista de platos vacía, plato ajeno al restaurante y creación de otro pedido activo para el mismo cliente. Solo se permite un pedido activo en PENDIENTE, EN_PREPARACION o LISTO.'),
('14. HU12 — Consultar bandeja de pedidos',[('Microservicio','Plazoleta'),('Endpoint','GET /api/v1/pedidos?estado=PENDIENTE&page=0&size=10'),('Rol requerido','EMPLEADO'),('Esperado','200 OK; solo pedidos del restaurante del empleado, con filtro/paginación.')],
'Inicia sesión como empleado de HU6, autoriza su JWT en Plazoleta y usa el pedido pendiente de HU11. No hay cuerpo JSON.',
'',
'Muestra el pedido en la respuesta y sus metadatos. Repite sin el parámetro estado para comprobar la bandeja sin filtro.',
'Prueba rol distinto de EMPLEADO y un empleado de otro restaurante; no debe consultar pedidos ajenos.'),
('15. HU13 — Asignarse e iniciar preparación',[('Microservicio','Plazoleta'),('Endpoint','PATCH /api/v1/pedidos/{pedidoId}/preparacion'),('Rol requerido','EMPLEADO del restaurante'),('Esperado','200 OK; estado EN_PREPARACION y empleado asignado.')],
'Usa empleadoId y pedidoId de las historias anteriores. No hay cuerpo JSON.',
'',
'Comprueba que el estado pase de PENDIENTE a EN_PREPARACION y que empleadoAsignado coincida con el empleado autenticado.',
'Intenta usar un pedido de otro restaurante o repetir la transición en un estado no permitido; debe rechazarse.'),
('16. HU14 — Marcar pedido listo',[('Microservicio','Plazoleta'),('Endpoint','PATCH /api/v1/pedidos/{pedidoId}/listo'),('Rol requerido','EMPLEADO asignado'),('Esperado','200 OK; estado LISTO y PIN de seis dígitos.')],
'Continúa con el pedido en EN_PREPARACION y el mismo empleado. No hay cuerpo JSON.',
'',
'Muestra estado LISTO y guarda el PIN devuelto para HU15. En consola aparecerá [AVISO SMS LOCAL]. Es una simulación: el proyecto no tiene credenciales para enviar SMS real.',
'Prueba marcar listo un pedido que no esté EN_PREPARACION o que corresponda a otro restaurante.'),
('17. HU15 — Entregar pedido con PIN',[('Microservicio','Plazoleta'),('Endpoint','PATCH /api/v1/pedidos/{pedidoId}/entregar'),('Rol requerido','EMPLEADO del restaurante'),('Esperado','200 OK; pasa de LISTO a ENTREGADO si el PIN es correcto.')],
'Usa el pedido LISTO de HU14 y el PIN real devuelto por esa operación.',
'{\n  "pinSeguridad": "REEMPLAZA_POR_EL_PIN_DE_HU14"\n}',
'Comprueba que la respuesta muestre estado ENTREGADO.',
'Prueba PIN incorrecto y pedido todavía no LISTO. Deben rechazarse y no marcar el pedido como ENTREGADO.'),
('18. HU16 — Cancelar pedido pendiente',[('Microservicio','Plazoleta'),('Endpoint','PATCH /api/v1/pedidos/{pedidoId}/cancelar'),('Rol requerido','CLIENTE dueño del pedido'),('Esperado','200 OK; cancelación permitida solo desde PENDIENTE.')],
'Crea un pedido adicional con el cliente de HU8 para que HU11 siga libre para el flujo completo. No hay cuerpo JSON.',
'',
'Con el cliente dueño cancela ese pedido mientras está PENDIENTE. Muestra el estado resultante. No canceles el pedido que usarás para completar HU13–HU15.',
'Intenta cancelar después de iniciar preparación y con un cliente diferente; ambas acciones deben rechazarse.'),
('19. HU17 — Consultar trazabilidad',[('Microservicio','Plazoleta'),('Endpoint','GET /api/v1/pedidos/{pedidoId}/trazabilidad'),('Rol requerido','CLIENTE dueño del pedido'),('Esperado','200 OK; lista de estados/fechas del pedido.')],
'Usa un pedido que ya haya cambiado de estado mediante HU13–HU15 o HU16. No hay cuerpo JSON.',
'',
'Comprueba que los eventos reflejen los cambios de estado y tengan fechas y usuarioId. Muestra la trazabilidad al cliente dueño.',
'Con un cliente distinto intenta consultar el mismo pedido; el historial debe quedar protegido.'),
('20. HU18 — Consultar eficiencia del restaurante',[('Microservicio','Plazoleta'),('Endpoint','GET /api/v1/restaurantes/{restauranteId}/eficiencia'),('Rol requerido','PROPIETARIO del restaurante'),('Esperado','200 OK; duración de pedidos entregados y ranking ascendente por promedio de empleado.')],
'Completa al menos un pedido mediante HU11–HU15 para que existan datos. Autoriza al propietario del restaurante. No hay cuerpo JSON.',
'',
'Muestra duraciones de pedidos entregados y el ranking ordenado de menor a mayor duración promedio por empleado.',
'Prueba restaurante ajeno. Para comparar empleados, completa pedidos con más de un empleado. Sin pedidos entregados, la respuesta no tendrá métricas útiles.')]

for title,meta,context,payload,check,negative in stories:
 heading(title,2)
 p(labelblock(meta))
 bodytext(context)
 if payload:code(payload)
 bodytext('Comprueba: '+check,'Comprueba: ')
 bodytext('Pruebas negativas recomendadas: '+negative,'Pruebas negativas recomendadas: ')

heading('21. Orden recomendado para demostrar el flujo completo',2)
p('HU1 → HU2 → HU3 → HU5 → HU6 → HU8 → HU9 → HU10 → HU11 → HU12 → HU13 → HU14 → HU15 → HU17 → HU18. Demuestra HU4 y HU7 como cambios del plato. Para HU16 usa un pedido separado que permanezca PENDIENTE. Guarda los IDs a medida que avanzas.')
heading('22. Códigos de respuesta que puedes encontrar',2)
compact('401 Unauthorized: falta JWT válido o las credenciales de login no son correctas.')
compact('403 Forbidden: el usuario autenticado tiene un rol que no puede ejecutar la operación.')
compact('400 Bad Request: dato inválido, paginación o transición de estado no permitida.')
compact('404 Not Found: recurso inexistente o que no corresponde al alcance del usuario.')
compact('409 Conflict: correo, documento o NIT duplicado, según la operación.')
p('El código concreto puede depender del controlador y del tipo de validación; registra la respuesta real que devuelve Swagger.')
heading('23. Lista final de verificación',2)
for n,name in enumerate(['Crear propietario adulto como administrador.','Crear restaurante con propietario válido.','Crear plato activo en restaurante propio.','Modificar solo precio/descripción.','Comprobar login y permisos JWT por rol.','Crear empleado asociado y probar login.','Desactivar y reactivar plato propio.','Crear cliente público y probar login.','Listar restaurantes ordenados y paginados.','Listar menú activo y filtrar categoría.','Crear pedido PENDIENTE y probar duplicado activo.','Consultar bandeja del empleado.','Iniciar preparación y asociar empleado.','Marcar listo y obtener PIN simulado.','Entregar pedido con PIN correcto e incorrecto.','Cancelar pedido propio solo PENDIENTE.','Consultar trazabilidad propia.','Consultar eficiencia como propietario.'],1):compact(f'☐ HU{n}: {name}')
p('Material del proyecto utilizado: README.md, docs/HU1-HU9.md, docs/guia-presentacion-HU1-HU18.md y controladores REST de Usuarios y Plazoleta.')
# Save to a new file; never overwrite the retained example.
out.parent.mkdir(parents=True,exist_ok=True);d.save(str(out));print(out.resolve())



