package br.com.metaltech.monitoramento.service;

import br.com.metaltech.monitoramento.dto.request.AnomaliaRequest;
import br.com.metaltech.monitoramento.dto.response.AnomaliaResponse;
import br.com.metaltech.monitoramento.entity.Anomalia;
import br.com.metaltech.monitoramento.repository.AnomaliaRepository;

import java.time.ZoneOffset;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service 
public class AnomaliaService {
    
    private final AnomaliaRepository anomaliaRepository;

    public AnomaliaService(AnomaliaRepository anomaliaRepository) {
        this.anomaliaRepository = anomaliaRepository;
    }

    @Transactional 
    public void registrar(AnomaliaRequest request) {
        boolean jaExiste = anomaliaRepository.existsByEquipamentoAndIdOrigem(request.equipamento(), request.idOrigem());

        if (jaExiste) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Essa anomalia já foi registrada para o equipamento");
        }

        var dataUtc = request.dataOcorrencia().withOffsetSameInstant(ZoneOffset.UTC).toLocalDateTime();

        Anomalia anomalia = new Anomalia(
            request.idOrigem(),
            request.tipo(),
            request.equipamento(),
            request.tipoReservatorio(),
            request.descricao(),
            request.severidade(),
            dataUtc
        );

        anomaliaRepository.save(anomalia);
    }

    @Transactional(readOnly = true) 
    public List<AnomaliaResponse> listarTodas() {
        return anomaliaRepository.findAllByOrderByDataOcorrenciaDesc()
            .stream()
            .map(anomalia -> new AnomaliaResponse(
                anomalia.getId(),
                anomalia.getIdOrigem(),
                anomalia.getTipo(),
                anomalia.getEquipamento(),
                anomalia.getTipoReservatorio(),
                anomalia.getDescricao(),
                anomalia.getSeveridade(),
                anomalia.getDataOcorrencia()
            ))
            .toList();
    }
}
