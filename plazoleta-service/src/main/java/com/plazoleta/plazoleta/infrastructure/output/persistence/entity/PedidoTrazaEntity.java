package com.plazoleta.plazoleta.infrastructure.output.persistence.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "pedido_trazas")
public class PedidoTrazaEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) private Long id;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "pedido_id") private PedidoEntity pedido;
    @Column(nullable = false, length = 24) private String estado;
    @Column(name = "usuario_id", nullable = false) private Long usuarioId;
    @Column(nullable = false) private LocalDateTime fecha;
    @Column(length = 500) private String observacion;

    public PedidoTrazaEntity() {}
    public PedidoTrazaEntity(PedidoEntity pedido, String estado, Long usuarioId, LocalDateTime fecha, String observacion) {
        this.pedido = pedido; this.estado = estado; this.usuarioId = usuarioId; this.fecha = fecha; this.observacion = observacion;
    }
    public Long getId() { return id; }
    public String getEstado() { return estado; }
    public Long getUsuarioId() { return usuarioId; }
    public LocalDateTime getFecha() { return fecha; }
    public String getObservacion() { return observacion; }
}
