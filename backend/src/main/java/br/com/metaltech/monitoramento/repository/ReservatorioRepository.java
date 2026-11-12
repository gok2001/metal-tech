package br.com.metaltech.monitoramento.repository;

import br.com.metaltech.monitoramento.entity.Reservatorio;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ReservatorioRepository extends JpaRepository<Reservatorio, Long> {
    
}
