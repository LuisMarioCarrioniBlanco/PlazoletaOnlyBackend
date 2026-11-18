package com.plazoleta.plazoleta.infrastructure.output.persistence.repository;

import com.plazoleta.plazoleta.infrastructure.output.persistence.entity.PedidoEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Collection;
import java.util.List;

public interface PedidoJpaRepository extends JpaRepository<PedidoEntity, Long> {
    Page<PedidoEntity> findByRestauranteIdAndEstado(Long restauranteId, String estado, Pageable pageable);
    Page<PedidoEntity> findByRestauranteId(Long restauranteId, Pageable pageable);
    List<PedidoEntity> findAllByRestauranteId(Long restauranteId);
    List<PedidoEntity> findByClienteIdAndEstadoIn(Long clienteId, Collection<String> estados);
    List<PedidoEntity> findByClienteId(Long clienteId);
}
