package com.plazoleta.plazoleta.infrastructure.output.persistence.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "pedido_items")
public class PedidoItemEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) private Long id;
    @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "pedido_id") private PedidoEntity pedido;
    @Column(name = "plato_id", nullable = false) private Long platoId;
    @Column(name = "nombre_plato", nullable = false, length = 120) private String nombrePlato;
    @Column(name = "precio_unitario", nullable = false) private Integer precioUnitario;
    @Column(nullable = false) private Integer cantidad;

    public PedidoItemEntity() {}
    public PedidoItemEntity(PedidoEntity pedido, Long platoId, String nombrePlato, Integer precioUnitario, Integer cantidad) {
        this.pedido = pedido; this.platoId = platoId; this.nombrePlato = nombrePlato;
        this.precioUnitario = precioUnitario; this.cantidad = cantidad;
    }
    public Long getId() { return id; }
    public PedidoEntity getPedido() { return pedido; }
    public Long getPlatoId() { return platoId; }
    public String getNombrePlato() { return nombrePlato; }
    public Integer getPrecioUnitario() { return precioUnitario; }
    public Integer getCantidad() { return cantidad; }
}
