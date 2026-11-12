package br.com.metaltech.monitoramento.repository;

import br.com.metaltech.monitoramento.enums.TipoPeca;
import br.com.metaltech.monitoramento.entity.Reservatorio;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ReservatorioRepository extends JpaRepository<Reservatorio, Long> {
    Optional<Reservatorio> findByTipoPeca(TipoPeca tipoPeca);
}
