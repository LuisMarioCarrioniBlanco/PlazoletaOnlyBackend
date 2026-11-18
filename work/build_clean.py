from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path
out=Path(r'docs/Guia_por_historia_Plazoleta_HU1-HU18.docx')
d=Document(); s=d.sections[0];s.top_margin=Inches(.72);s.bottom_margin=Inches(.72);s.left_margin=Inches(.82);s.right_margin=Inches(.82)
normal=d.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(10.5);normal.paragraph_format.space_after=Pt(4);normal.paragraph_format.line_spacing=1.05
for name,size in [('Title',22),('Heading 1',15),('Heading 2',12)]:
 st=d.styles[name];st.font.name='Calibri';st.font.size=Pt(size);st.font.bold=True;st.font.color.rgb=RGBColor(31,78,121);st.paragraph_format.space_before=Pt(8);st.paragraph_format.space_after=Pt(3);st.paragraph_format.keep_with_next=True

def para(label,text,style=None):
 x=d.add_paragraph(style=style)
 if label:
  r=x.add_run(label);r.bold=True
 x.add_run(text)
 return x

d.add_paragraph('Guía de implementación y demostración por historia',style='Title')
para('', 'Backend Plazoleta de Comidas · HU1–HU18')
para('', 'En cada historia encontrarás qué comportamiento construir o revisar y qué ejecutar para demostrarlo. Las rutas corresponden a los controladores del proyecto. Usa Swagger de Usuarios en http://localhost:8081/swagger-ui.html y Swagger de Plazoleta en http://localhost:8082/swagger-ui.html.')
d.add_heading('Preparación para la demostración',1)
para('1. Inicia los servicios. ','Abre dos terminales y ejecuta mvn spring-boot:run dentro de usuarios-service y plazoleta-service.')
para('2. Autentica cada rol. ','En Usuarios ejecuta POST /api/v1/auth/login. Pulsa Authorize en cada Swagger por separado y vuelve a autorizar al cambiar de usuario. No compartas el JWT completo.')
para('3. Conserva los identificadores. ','Anota propietarioId, restauranteId, platoId, empleadoId, clienteId y pedidoId conforme los vayas creando. Para nuevas pruebas usa correo, documento y NIT únicos.')
para('Administrador inicial. ','El README indica admin@plazoleta.local y Admin123!, salvo que hayan configurado INITIAL_ADMIN_EMAIL o INITIAL_ADMIN_PASSWORD.')

d.add_heading('HU1–HU9 · Usuarios, restaurante y platos',1)
items=[
('HU1 · Crear propietario','Implementa el alta solo para ADMINISTRADOR en Usuarios. Valida correo y documento únicos, documento numérico, celular de hasta 13 caracteres, fecha válida y edad mínima de 18 años; cifra la clave con BCrypt y asigna rol PROPIETARIO.','Con token administrador ejecuta POST /api/v1/usuarios/propietarios con datos nuevos. Muestra la respuesta con rol PROPIETARIO y guarda el id. Repite con fecha de menor de edad para mostrar rechazo; prueba también correo/documento duplicados o token sin permiso.'),
('HU2 · Crear restaurante','En Plazoleta, permite crear restaurantes solo al ADMINISTRADOR. Valida NIT numérico y único, nombre no compuesto solo por números, y consulta Usuarios para confirmar que propietarioId corresponde a un usuario PROPIETARIO existente.','Con token administrador ejecuta POST /api/v1/restaurantes con nombre, NIT, dirección, teléfono, urlLogo y propietarioId de HU1. Muestra el id y propietarioId guardados. Prueba NIT duplicado y propietario inexistente o de otro rol.'),
('HU3 · Crear plato','Permite que el propietario del restaurante cree un plato, con campos requeridos y precio entero mayor que cero. El plato queda ligado al restaurante y activo=true.','Con token del propietario ejecuta POST /api/v1/restaurantes/{restauranteId}/platos con nombre, precio, descripción, urlImagen y categoría. Muestra activo=true y guarda platoId. Prueba precio cero/negativo y un token de otro propietario.'),
('HU4 · Modificar plato','Permite al propietario cambiar únicamente precio y descripción. La operación no debe alterar nombre, categoría, URL de imagen, restaurante ni estado activo.','Antes de ejecutar, anota los datos actuales. Envía PATCH /api/v1/restaurantes/{restauranteId}/platos/{platoId} con precio y descripción nuevos. Muestra los campos cambiados y compara que los demás sigan iguales. Prueba plato ajeno y precio inválido.'),
('HU5 · Iniciar sesión y autorizar','Verifica correo y clave con BCrypt; emite un JWT compartido por ambos servicios y usa el rol del token para permitir o denegar rutas.','Envía POST /api/v1/auth/login con credenciales válidas; muestra tipo Bearer, correo e id/rol y oculta el valor del token en capturas. Prueba la clave incorrecta (401) y un rol que intente usar una operación prohibida.'),
('HU6 · Crear empleado','Solo el propietario del restaurante puede crear empleados para ese restaurante. La cuenta debe tener documento/correo únicos, rol EMPLEADO, restauranteId asociado y clave cifrada. Plazoleta coordina el alta con Usuarios mediante el endpoint interno protegido por X-Internal-Token.','Con token propietario ejecuta POST /api/v1/restaurantes/{restauranteId}/empleados y muestra rol EMPLEADO y restauranteId. Después inicia sesión con ese empleado y muestra su rol. Prueba restaurante ajeno y correo/documento repetidos.'),
('HU7 · Cambiar estado del plato','Permite al propietario activar o desactivar un plato de su restaurante; confirma que el plato pertenece al restaurante indicado y cambia solo activo.','Ejecuta PATCH /api/v1/restaurantes/{restauranteId}/platos/{platoId}/estado con activo=false y luego true. Muestra ambas respuestas. Prueba el plato de otro restaurante. Después usa HU10 para evidenciar que el plato inactivo no aparece en el menú.'),
('HU8 · Registrar cliente','El registro es público, requiere los datos definidos, impide duplicar correo/documento, fija rol CLIENTE y cifra la clave. El solicitante no elige el rol.','Sin token ejecuta POST /api/v1/usuarios/clientes con datos nuevos. Muestra el rol CLIENTE e inicia sesión con esa cuenta. Prueba correo/documento duplicados. Conserva clienteId para las historias de consulta y pedidos.'),
('HU9 · Listar restaurantes','Solo CLIENTE puede consultar. La lista va ordenada por nombre ascendente y valida page≥0 y size entre 1 y 100; devuelve nombre, urlLogo y metadatos de paginación.','Con token cliente ejecuta GET /api/v1/restaurantes?page=0&size=10. Muestra orden alfabético y page, size, totalElements y totalPages. Consulta otra página, luego prueba page negativo, size fuera de rango y token de otro rol.')]

def story(h,imp,show):
 d.add_heading(h,2)
 para('Implementa o revisa: ',imp)
 para('Ejecuta y muestra: ',show)
for x in items:story(*x)

d.add_heading('HU10–HU18 · Menú y ciclo de pedidos',1)
items2=[
('HU10 · Consultar menú','GET /api/v1/restaurantes/{restauranteId}/platos permite CLIENTE; lista solo platos activos, puede filtrar por categoría y pagina resultados.','Con token cliente ejecuta la ruta con ?page=0&size=10. Muestra el plato activo de HU3 y los metadatos. Añade &categoria= seguido de la categoría creada. Desactiva el plato con HU7 y repite para mostrar que desapareció.'),
('HU11 · Crear pedido','POST /api/v1/pedidos permite CLIENTE; valida restaurante y platos/cantidades positivas, asociación del plato al restaurante y máximo un pedido activo por cliente en PENDIENTE, EN_PREPARACION o LISTO. El nuevo pedido inicia PENDIENTE.','Envía restauranteId y platos con platoId/cantidad. Muestra pedidoId, artículos y estado PENDIENTE. Intenta crear un segundo pedido activo con el mismo cliente para demostrar el rechazo. Para repetir HU11, completa HU13–HU15 o cancela mientras siga pendiente.'),
('HU12 · Consultar bandeja del empleado','GET /api/v1/pedidos es solo para EMPLEADO; muestra pedidos del restaurante asociado, con filtro estado opcional y paginación.','Con token del empleado de HU6 ejecuta ?estado=PENDIENTE&page=0&size=10. Muestra el pedido de HU11 y metadatos. Consulta también sin estado. Comprueba que otro restaurante no se filtra en la bandeja.'),
('HU13 · Iniciar preparación','PATCH /api/v1/pedidos/{pedidoId}/preparacion permite al empleado autorizado tomar el pedido pendiente, asociar su usuario y cambiarlo a EN_PREPARACION.','Con el empleado del restaurante ejecuta la ruta sobre pedidoId. Muestra EN_PREPARACION y empleadoAsignado correcto. Intenta una transición repetida o pedido de otro restaurante y muestra el rechazo.'),
('HU14 · Marcar listo','PATCH /api/v1/pedidos/{pedidoId}/listo permite transición desde EN_PREPARACION a LISTO y genera un PIN de seis dígitos necesario para la entrega. El aviso SMS es simulado localmente.','Con el mismo empleado ejecuta la ruta. Muestra estado LISTO y copia el PIN devuelto para HU15. Enseña el registro [AVISO SMS LOCAL] en consola y aclara que el proyecto no envía SMS real.'),
('HU15 · Entregar con PIN','PATCH /api/v1/pedidos/{pedidoId}/entregar acepta solo pedidos LISTO y valida pinSeguridad antes de pasar a ENTREGADO.','Con token empleado envía el PIN real recibido en HU14. Muestra estado ENTREGADO. Prueba un PIN incorrecto y un pedido todavía no LISTO; deben rechazarse sin marcar como entregados.'),
('HU16 · Cancelar pedido','PATCH /api/v1/pedidos/{pedidoId}/cancelar solo permite al cliente dueño cancelar mientras el pedido siga PENDIENTE.','Crea un pedido aparte y cancélalo con el cliente dueño mientras está PENDIENTE; muestra el nuevo estado. En otro pedido inicia preparación con HU13 y luego intenta cancelarlo para mostrar el rechazo. Prueba también con otro cliente.'),
('HU17 · Consultar trazabilidad','GET /api/v1/pedidos/{pedidoId}/trazabilidad devuelve los estados y fechas del pedido solo al cliente dueño.','Con cliente dueño consulta un pedido que haya avanzado por HU13–HU14 (o cancelado por HU16). Muestra los eventos, usuarioId, fecha y observación. Repite con otro cliente y muestra que no puede consultar el historial.'),
('HU18 · Consultar eficiencia','GET /api/v1/restaurantes/{restauranteId}/eficiencia es solo para el propietario. Muestra duración de pedidos entregados y ranking ascendente por duración promedio de empleado.','Completa al menos un pedido mediante HU11–HU15. Con token propietario consulta la ruta y muestra las duraciones y el ranking. Prueba un restaurante ajeno. Si comparas empleados, completa pedidos con más de un empleado.')]
for x in items2:story(*x)

d.add_heading('Orden para mostrar el proyecto completo',1)
para('', 'HU1 → HU2 → HU3 → HU5 → HU6 → HU8 → HU9 → HU10 → HU11 → HU12 → HU13 → HU14 → HU15 → HU17 → HU18. Demuestra HU4 y HU7 como cambios al plato. Para HU16 usa un pedido separado que siga PENDIENTE.')
d.add_heading('Evidencia y respuestas de error',1)
para('', 'En cada historia guarda la ruta, rol utilizado, resultado esperado y respuesta observada; oculta JWT y claves. La guía del proyecto menciona 401 para autenticación/credenciales, 403 para rol, 400 para regla o dato inválido, 404 para recurso inexistente o ajeno y 409 para duplicados. Verifica el código realmente devuelto por cada operación.')
para('', 'Fuente de los pasos: README.md, docs/HU1-HU9.md, docs/guia-presentacion-HU1-HU18.md y controladores REST de Usuarios y Plazoleta.')
f=s.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER;f.add_run('Plazoleta Backend · Guía HU1–HU18')
d.save(out); print(out.resolve())
