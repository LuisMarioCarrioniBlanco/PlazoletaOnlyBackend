package com.plazoleta.plazoleta.application.service;

import com.plazoleta.plazoleta.application.port.output.UsuariosPort;
import com.plazoleta.plazoleta.domain.exception.RecursoNoEncontradoException;
import com.plazoleta.plazoleta.domain.exception.ReglaNegocioException;
import com.plazoleta.plazoleta.domain.model.EstadoPedido;
import com.plazoleta.plazoleta.infrastructure.output.persistence.entity.*;
import com.plazoleta.plazoleta.infrastructure.output.persistence.repository.*;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.security.SecureRandom;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;

@Service
public class PedidoService {
    private static final List<String> ACTIVOS = List.of("PENDIENTE", "EN_PREPARACION", "LISTO");
    private final PedidoJpaRepository pedidos;
    private final RestauranteJpaRepository restaurantes;
    private final PlatoJpaRepository platos;
    private final UsuariosPort usuarios;
    private final SecureRandom random = new SecureRandom();

    public PedidoService(PedidoJpaRepository pedidos, RestauranteJpaRepository restaurantes,
                        PlatoJpaRepository platos, UsuariosPort usuarios) {
        this.pedidos = pedidos; this.restaurantes = restaurantes; this.platos = platos; this.usuarios = usuarios;
    }

    @Transactional(readOnly = true)
    public Page<PlatoResumen> listarMenu(Long restauranteId, String categoria, int page, int size) {
        validarPagina(page, size);
        if (!restaurantes.existsById(restauranteId)) throw new RecursoNoEncontradoException("No existe el restaurante indicado");
        var request = PageRequest.of(page, size, Sort.by("nombre").ascending());
        Page<PlatoEntity> resultado = categoria == null || categoria.isBlank()
                ? platos.findByRestauranteIdAndActivoTrue(restauranteId, request)
                : platos.findByRestauranteIdAndActivoTrueAndCategoriaIgnoreCase(restauranteId, categoria.trim(), request);
        return resultado.map(p -> new PlatoResumen(p.getId(), p.getNombre(), p.getPrecio(), p.getDescripcion(),
                p.getUrlImagen(), p.getCategoria(), p.getRestauranteId()));
    }

    @Transactional
    public PedidoEntity crear(Long clienteId, Long restauranteId, List<ItemSolicitado> seleccion) {
        if (!restaurantes.existsById(restauranteId)) throw new RecursoNoEncontradoException("No existe el restaurante indicado");
        if (seleccion == null || seleccion.isEmpty()) throw new ReglaNegocioException("El pedido debe incluir al menos un plato");
        if (seleccion.stream().map(ItemSolicitado::platoId).distinct().count() != seleccion.size())
            throw new ReglaNegocioException("Cada plato debe aparecer una sola vez en la lista del pedido");
        LocalDateTime ahora = LocalDateTime.now();
        PedidoEntity pedido = new PedidoEntity();
        pedido.setClienteId(clienteId); pedido.setRestauranteId(restauranteId);
        pedido.setEstado(EstadoPedido.PENDIENTE.name()); pedido.setCreadoEn(ahora); pedido.setActualizadoEn(ahora);
        pedido.getTrazas().add(new PedidoTrazaEntity(pedido, EstadoPedido.PENDIENTE.name(), clienteId, ahora, "Pedido creado"));
        for (ItemSolicitado item : seleccion) {
            if (item.platoId() == null || item.cantidad() == null || item.cantidad() < 1)
                throw new ReglaNegocioException("Cada plato debe tener un ID y una cantidad mayor que cero");
            PlatoEntity plato = platos.findById(item.platoId())
                    .orElseThrow(() -> new RecursoNoEncontradoException("No existe el plato " + item.platoId()));
            if (!plato.getRestauranteId().equals(restauranteId)) throw new ReglaNegocioException("Todos los platos deben pertenecer al restaurante seleccionado");
            if (!plato.isActivo()) throw new ReglaNegocioException("El plato " + plato.getNombre() + " no está disponible");
            pedido.getItems().add(new PedidoItemEntity(pedido, plato.getId(), plato.getNombre(), plato.getPrecio(), item.cantidad()));
        }
        if (!pedidos.findByClienteIdAndEstadoIn(clienteId, ACTIVOS).isEmpty())
            throw new ReglaNegocioException("Ya tienes un pedido pendiente o en preparación; espera a que sea entregado o cancelado");
        return pedidos.save(pedido);
    }

    @Transactional(readOnly = true)
    public Page<PedidoEntity> listarParaEmpleado(Long empleadoId, String estado, int page, int size) {
        validarPagina(page, size);
        Long restauranteId = obtenerRestauranteEmpleado(empleadoId);
        if (estado == null || estado.isBlank()) return pedidos.findByRestauranteId(restauranteId,
                PageRequest.of(page, size, Sort.by("creadoEn").ascending()));
        return pedidos.findByRestauranteIdAndEstado(restauranteId, parseEstado(estado).name(),
                PageRequest.of(page, size, Sort.by("creadoEn").ascending()));
    }

    @Transactional
    public PedidoEntity iniciarPreparacion(Long empleadoId, Long pedidoId) {
        Long restauranteId = obtenerRestauranteEmpleado(empleadoId);
        PedidoEntity pedido = pedidoEnRestaurante(pedidoId, restauranteId);
        exigirEstado(pedido, EstadoPedido.PENDIENTE);
        pedido.setEmpleadoId(empleadoId);
        cambiarEstado(pedido, EstadoPedido.EN_PREPARACION, empleadoId, "Empleado asignado e inició la preparación");
        return pedidos.save(pedido);
    }

    @Transactional
    public PedidoEntity marcarListo(Long empleadoId, Long pedidoId) {
        Long restauranteId = obtenerRestauranteEmpleado(empleadoId);
        PedidoEntity pedido = pedidoEnRestaurante(pedidoId, restauranteId);
        exigirAsignado(pedido, empleadoId); exigirEstado(pedido, EstadoPedido.EN_PREPARACION);
        String pin = String.format(Locale.ROOT, "%06d", random.nextInt(1_000_000));
        pedido.setPinSeguridad(pin);
        cambiarEstado(pedido, EstadoPedido.LISTO, empleadoId, "Aviso local simulado enviado; PIN de recogida generado");
        PedidoEntity guardado = pedidos.save(pedido);
        System.out.printf("[AVISO SMS LOCAL] Pedido %d listo. PIN de recogida: %s%n", pedidoId, pin);
        return guardado;
    }

    @Transactional
    public PedidoEntity entregar(Long empleadoId, Long pedidoId, String pin) {
        Long restauranteId = obtenerRestauranteEmpleado(empleadoId);
        PedidoEntity pedido = pedidoEnRestaurante(pedidoId, restauranteId);
        exigirAsignado(pedido, empleadoId); exigirEstado(pedido, EstadoPedido.LISTO);
        if (pin == null || !pin.equals(pedido.getPinSeguridad())) throw new ReglaNegocioException("El PIN de seguridad no es correcto");
        cambiarEstado(pedido, EstadoPedido.ENTREGADO, empleadoId, "Pedido entregado al cliente");
        return pedidos.save(pedido);
    }

    @Transactional
    public PedidoEntity cancelar(Long clienteId, Long pedidoId) {
        PedidoEntity pedido = pedidos.findById(pedidoId)
                .orElseThrow(() -> new RecursoNoEncontradoException("No existe el pedido indicado"));
        if (!pedido.getClienteId().equals(clienteId)) throw new RecursoNoEncontradoException("No existe el pedido indicado");
        if (!EstadoPedido.PENDIENTE.name().equals(pedido.getEstado()))
            throw new ReglaNegocioException("Lo sentimos, tu pedido ya está en preparación y no puede cancelarse");
        cambiarEstado(pedido, EstadoPedido.CANCELADO, clienteId, "Pedido cancelado por el cliente");
        return pedidos.save(pedido);
    }

    @Transactional(readOnly = true)
    public List<PedidoTrazaEntity> trazabilidad(Long clienteId, Long pedidoId) {
        PedidoEntity pedido = pedidos.findById(pedidoId)
                .orElseThrow(() -> new RecursoNoEncontradoException("No existe el pedido indicado"));
        if (!pedido.getClienteId().equals(clienteId)) throw new RecursoNoEncontradoException("No existe el pedido indicado");
        return pedido.getTrazas();
    }

    @Transactional(readOnly = true)
    public EficienciaRestaurante eficiencia(Long propietarioId, Long restauranteId) {
        RestauranteEntity restaurante = restaurantes.findById(restauranteId)
                .orElseThrow(() -> new RecursoNoEncontradoException("No existe el restaurante indicado"));
        if (!restaurante.getPropietarioId().equals(propietarioId)) throw new ReglaNegocioException("Solo el propietario puede consultar la eficiencia de su restaurante");
        Map<Long, List<Long>> duraciones = new HashMap<>();
        List<PedidoDuracion> pedidosEntregados = new ArrayList<>();
        pedidos.findAllByRestauranteId(restauranteId).forEach(p -> {
            if (EstadoPedido.ENTREGADO.name().equals(p.getEstado()) && p.getEmpleadoId() != null) {
                LocalDateTime fin = p.getTrazas().stream().filter(t -> EstadoPedido.ENTREGADO.name().equals(t.getEstado()))
                        .map(PedidoTrazaEntity::getFecha).max(LocalDateTime::compareTo).orElse(p.getActualizadoEn());
                long segundos = Math.max(0, Duration.between(p.getCreadoEn(), fin).getSeconds());
                pedidosEntregados.add(new PedidoDuracion(p.getId(), p.getEmpleadoId(), p.getCreadoEn(), fin, segundos));
                duraciones.computeIfAbsent(p.getEmpleadoId(), ignored -> new ArrayList<>()).add(segundos);
            }
        });
        List<EficienciaEmpleado> ranking = duraciones.entrySet().stream().map(e -> new EficienciaEmpleado(e.getKey(), e.getValue().size(),
                        Math.round(e.getValue().stream().mapToLong(Long::longValue).average().orElse(0))))
                .sorted(Comparator.comparingLong(EficienciaEmpleado::tiempoPromedioSegundos)).toList();
        return new EficienciaRestaurante(pedidosEntregados, ranking);
    }

    private Long obtenerRestauranteEmpleado(Long empleadoId) {
        var empleado = usuarios.buscarPorId(empleadoId);
        if (!"EMPLEADO".equals(empleado.rol()) || empleado.restauranteId() == null)
            throw new ReglaNegocioException("La cuenta no está asociada a un restaurante como empleado");
        return empleado.restauranteId();
    }
    private PedidoEntity pedidoEnRestaurante(Long pedidoId, Long restauranteId) {
        PedidoEntity pedido = pedidos.findById(pedidoId).orElseThrow(() -> new RecursoNoEncontradoException("No existe el pedido indicado"));
        if (!pedido.getRestauranteId().equals(restauranteId)) throw new RecursoNoEncontradoException("No existe el pedido indicado");
        return pedido;
    }
    private void exigirAsignado(PedidoEntity pedido, Long empleadoId) {
        if (!Objects.equals(pedido.getEmpleadoId(), empleadoId)) throw new ReglaNegocioException("El pedido debe estar asignado a este empleado");
    }
    private void exigirEstado(PedidoEntity pedido, EstadoPedido esperado) {
        if (!esperado.name().equals(pedido.getEstado())) throw new ReglaNegocioException("El pedido debe estar en estado " + esperado.name());
    }
    private void cambiarEstado(PedidoEntity pedido, EstadoPedido estado, Long usuarioId, String observacion) {
        LocalDateTime ahora = LocalDateTime.now();
        pedido.setEstado(estado.name()); pedido.setActualizadoEn(ahora);
        pedido.getTrazas().add(new PedidoTrazaEntity(pedido, estado.name(), usuarioId, ahora, observacion));
    }
    private EstadoPedido parseEstado(String estado) {
        try { return EstadoPedido.valueOf(estado.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_')); }
        catch (IllegalArgumentException ex) { throw new ReglaNegocioException("Estado inválido. Usa PENDIENTE, EN_PREPARACION, LISTO, ENTREGADO o CANCELADO"); }
    }
    private void validarPagina(int page, int size) {
        if (page < 0 || size < 1 || size > 100) throw new ReglaNegocioException("La página debe ser no negativa y el tamaño debe estar entre 1 y 100");
    }

    public record ItemSolicitado(Long platoId, Integer cantidad) {}
    public record PlatoResumen(Long id, String nombre, Integer precio, String descripcion,
                               String urlImagen, String categoria, Long restauranteId) {}
    public record EficienciaEmpleado(Long empleadoId, int pedidosEntregados, long tiempoPromedioSegundos) {}
    public record PedidoDuracion(Long pedidoId, Long empleadoId, LocalDateTime iniciadoEn,
                                 LocalDateTime terminadoEn, long duracionSegundos) {}
    public record EficienciaRestaurante(List<PedidoDuracion> pedidosEntregados, List<EficienciaEmpleado> rankingEmpleados) {}
}
