package br.com.metaltech.monitoramento.repository;

import br.com.metaltech.monitoramento.entity.ContagemIntervalo;

import java.time.LocalDateTime;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ContagemIntervaloRepository extends JpaRepository<ContagemIntervalo, Long> {
    boolean existsByInicioIntervalo(LocalDateTime inicioIntervalo);
}
