package com.plazoleta.plazoleta.infrastructure.input.rest;

import com.plazoleta.plazoleta.application.service.PedidoService;
import com.plazoleta.plazoleta.domain.model.EstadoPedido;
import com.plazoleta.plazoleta.infrastructure.input.rest.security.JwtPrincipal;
import com.plazoleta.plazoleta.infrastructure.output.persistence.entity.*;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/v1")
@SecurityRequirement(name = "bearerAuth")
public class PedidoController {
    private final PedidoService servicio;
    public PedidoController(PedidoService servicio) { this.servicio = servicio; }

    @GetMapping("/restaurantes/{restauranteId}/platos")
    @PreAuthorize("hasRole('CLIENTE')")
    public PaginaDto<PedidoService.PlatoResumen> listarMenu(@PathVariable Long restauranteId,
            @RequestParam(required = false) String categoria,
            @RequestParam(defaultValue = "0") int page, @RequestParam(defaultValue = "10") int size) {
        return PaginaDto.desde(servicio.listarMenu(restauranteId, categoria, page, size));
    }

    @PostMapping("/pedidos")
    @PreAuthorize("hasRole('CLIENTE')")
    @ResponseStatus(HttpStatus.CREATED)
    public PedidoResponse crear(@AuthenticationPrincipal JwtPrincipal principal, @Valid @RequestBody CrearPedidoRequest request) {
        return PedidoResponse.desde(servicio.crear(principal.id(), request.restauranteId(),
                request.platos().stream().map(p -> new PedidoService.ItemSolicitado(p.platoId(), p.cantidad())).toList()), false);
    }

    @GetMapping("/pedidos")
    @PreAuthorize("hasRole('EMPLEADO')")
    public PaginaDto<PedidoResponse> listarPedidos(@AuthenticationPrincipal JwtPrincipal principal,
            @RequestParam(required = false) String estado,
            @RequestParam(defaultValue = "0") int page, @RequestParam(defaultValue = "10") int size) {
        return PaginaDto.desde(servicio.listarParaEmpleado(principal.id(), estado, page, size)
                .map(p -> PedidoResponse.desde(p, false)));
    }

    @PatchMapping("/pedidos/{pedidoId}/preparacion")
    @PreAuthorize("hasRole('EMPLEADO')")
    public PedidoResponse iniciarPreparacion(@AuthenticationPrincipal JwtPrincipal principal, @PathVariable Long pedidoId) {
        return PedidoResponse.desde(servicio.iniciarPreparacion(principal.id(), pedidoId), false);
    }

    @PatchMapping("/pedidos/{pedidoId}/listo")
    @PreAuthorize("hasRole('EMPLEADO')")
    public PedidoResponse marcarListo(@AuthenticationPrincipal JwtPrincipal principal, @PathVariable Long pedidoId) {
        return PedidoResponse.desde(servicio.marcarListo(principal.id(), pedidoId), true);
    }

    @PatchMapping("/pedidos/{pedidoId}/entregar")
    @PreAuthorize("hasRole('EMPLEADO')")
    public PedidoResponse entregar(@AuthenticationPrincipal JwtPrincipal principal, @PathVariable Long pedidoId,
                                   @Valid @RequestBody EntregarRequest request) {
        return PedidoResponse.desde(servicio.entregar(principal.id(), pedidoId, request.pinSeguridad()), false);
    }

    @PatchMapping("/pedidos/{pedidoId}/cancelar")
    @PreAuthorize("hasRole('CLIENTE')")
    public PedidoResponse cancelar(@AuthenticationPrincipal JwtPrincipal principal, @PathVariable Long pedidoId) {
        return PedidoResponse.desde(servicio.cancelar(principal.id(), pedidoId), false);
    }

    @GetMapping("/pedidos/{pedidoId}/trazabilidad")
    @PreAuthorize("hasRole('CLIENTE')")
    public List<TrazaResponse> trazabilidad(@AuthenticationPrincipal JwtPrincipal principal, @PathVariable Long pedidoId) {
        return servicio.trazabilidad(principal.id(), pedidoId).stream()
                .map(t -> new TrazaResponse(t.getEstado(), t.getUsuarioId(), t.getFecha(), t.getObservacion())).toList();
    }

    @GetMapping("/restaurantes/{restauranteId}/eficiencia")
    @PreAuthorize("hasRole('PROPIETARIO')")
    public PedidoService.EficienciaRestaurante eficiencia(@AuthenticationPrincipal JwtPrincipal principal,
                                                              @PathVariable Long restauranteId) {
        return servicio.eficiencia(principal.id(), restauranteId);
    }

    public record CrearPedidoRequest(@NotNull @Positive Long restauranteId,
                                     @NotEmpty List<@Valid PlatoSolicitado> platos) {}
    public record PlatoSolicitado(@NotNull @Positive Long platoId, @NotNull @Positive Integer cantidad) {}
    public record EntregarRequest(@NotNull String pinSeguridad) {}
    public record TrazaResponse(String estado, Long usuarioId, LocalDateTime fecha, String observacion) {}
    public record PaginaDto<T>(List<T> content, int page, int size, long totalElements, int totalPages) {
        static <T> PaginaDto<T> desde(Page<T> p) {
            return new PaginaDto<>(p.getContent(), p.getNumber(), p.getSize(), p.getTotalElements(), p.getTotalPages());
        }
    }
    public record PedidoItemResponse(Long platoId, String nombrePlato, Integer precioUnitario, Integer cantidad) {}
    public record PedidoResponse(Long id, Long clienteId, Long restauranteId, Long empleadoAsignado,
            String estado, List<PedidoItemResponse> platos, LocalDateTime creadoEn,
            LocalDateTime actualizadoEn, String pinSeguridad) {
        static PedidoResponse desde(PedidoEntity p, boolean mostrarPin) {
            List<PedidoItemResponse> items = p.getItems().stream().map(i -> new PedidoItemResponse(
                    i.getPlatoId(), i.getNombrePlato(), i.getPrecioUnitario(), i.getCantidad())).toList();
            return new PedidoResponse(p.getId(), p.getClienteId(), p.getRestauranteId(), p.getEmpleadoId(),
                    p.getEstado(), items, p.getCreadoEn(), p.getActualizadoEn(), mostrarPin ? p.getPinSeguridad() : null);
        }
    }
}
