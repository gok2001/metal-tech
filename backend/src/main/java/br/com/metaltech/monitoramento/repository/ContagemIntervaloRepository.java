package br.com.metaltech.monitoramento.repository;

import br.com.metaltech.monitoramento.entity.ContagemIntervalo;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ContagemIntervaloRepository extends JpaRepository<ContagemIntervalo, Long> {
    
}
