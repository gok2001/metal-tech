package br.com.metaltech.monitoramento.repository;

import br.com.metaltech.monitoramento.entity.Anomalia;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

public interface AnomaliaRepository extends JpaRepository<Anomalia, Long> {
    boolean existsByEquipamentoAndIdOrigem(String equipamento, String idOrigem);

    List<Anomalia> findAllByOrderByDataOcorrenciaDesc();
}
