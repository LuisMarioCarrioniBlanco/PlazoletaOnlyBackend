package com.plazoleta.plazoleta.infrastructure.output.persistence.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "pedidos")
public class PedidoEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "cliente_id", nullable = false) private Long clienteId;
    @Column(name = "restaurante_id", nullable = false) private Long restauranteId;
    @Column(name = "empleado_id") private Long empleadoId;
    @Column(nullable = false, length = 24) private String estado;
    @Column(name = "pin_seguridad", length = 6) private String pinSeguridad;
    @Column(name = "creado_en", nullable = false) private LocalDateTime creadoEn;
    @Column(name = "actualizado_en", nullable = false) private LocalDateTime actualizadoEn;
    @OneToMany(mappedBy = "pedido", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.EAGER)
    @OrderBy("id ASC") private List<PedidoItemEntity> items = new ArrayList<>();
    @OneToMany(mappedBy = "pedido", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.EAGER)
    @OrderBy("fecha ASC") private List<PedidoTrazaEntity> trazas = new ArrayList<>();

    public PedidoEntity() {}
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getClienteId() { return clienteId; }
    public void setClienteId(Long clienteId) { this.clienteId = clienteId; }
    public Long getRestauranteId() { return restauranteId; }
    public void setRestauranteId(Long restauranteId) { this.restauranteId = restauranteId; }
    public Long getEmpleadoId() { return empleadoId; }
    public void setEmpleadoId(Long empleadoId) { this.empleadoId = empleadoId; }
    public String getEstado() { return estado; }
    public void setEstado(String estado) { this.estado = estado; }
    public String getPinSeguridad() { return pinSeguridad; }
    public void setPinSeguridad(String pinSeguridad) { this.pinSeguridad = pinSeguridad; }
    public LocalDateTime getCreadoEn() { return creadoEn; }
    public void setCreadoEn(LocalDateTime creadoEn) { this.creadoEn = creadoEn; }
    public LocalDateTime getActualizadoEn() { return actualizadoEn; }
    public void setActualizadoEn(LocalDateTime actualizadoEn) { this.actualizadoEn = actualizadoEn; }
    public List<PedidoItemEntity> getItems() { return items; }
    public List<PedidoTrazaEntity> getTrazas() { return trazas; }
}
