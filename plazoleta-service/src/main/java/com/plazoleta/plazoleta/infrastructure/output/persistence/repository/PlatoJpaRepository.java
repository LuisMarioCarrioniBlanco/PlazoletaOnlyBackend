package com.plazoleta.plazoleta.infrastructure.output.persistence.repository;

import com.plazoleta.plazoleta.infrastructure.output.persistence.entity.PlatoEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface PlatoJpaRepository extends JpaRepository<PlatoEntity, Long> {
    Page<PlatoEntity> findByRestauranteIdAndActivoTrue(Long restauranteId, Pageable pageable);
    Page<PlatoEntity> findByRestauranteIdAndActivoTrueAndCategoriaIgnoreCase(
            Long restauranteId, String categoria, Pageable pageable);
}
