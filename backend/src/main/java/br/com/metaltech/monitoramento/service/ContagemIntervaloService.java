package br.com.metaltech.monitoramento.service;

import br.com.metaltech.monitoramento.dto.request.ContagemIntervaloRequest;
import br.com.metaltech.monitoramento.dto.response.ContagemIntervaloHistoricoResponse;
import br.com.metaltech.monitoramento.dto.response.ContagemIntervaloResponse;
import br.com.metaltech.monitoramento.entity.ContagemIntervalo;
import br.com.metaltech.monitoramento.entity.Reservatorio;
import br.com.metaltech.monitoramento.enums.TipoPeca;
import br.com.metaltech.monitoramento.repository.ContagemIntervaloRepository;
import br.com.metaltech.monitoramento.repository.ReservatorioRepository;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service 
public class ContagemIntervaloService {

    private final ContagemIntervaloRepository contagemRepository;
    private final ReservatorioRepository reservatorioRepository;

    public ContagemIntervaloService(
        ContagemIntervaloRepository contagemRepository,
        ReservatorioRepository reservatorioRepository
    ) {
        this.contagemRepository = contagemRepository;
        this.reservatorioRepository = reservatorioRepository;
    }

    @Transactional 
    public ContagemIntervaloResponse registrar(ContagemIntervaloRequest request) {
        if (contagemRepository.existsByInicioIntervalo(request.inicioIntervalo())) {
            throw new IllegalArgumentException("Já existe uma contagem para esse horário");
        }

        Reservatorio metalico = reservatorioRepository
            .findByTipoPeca(TipoPeca.METALICA)
            .orElseThrow(() -> new IllegalStateException(
                "O reservatório de peças metálicas não foi configurado"
            ));
        
        Reservatorio naoMetalico = reservatorioRepository
            .findByTipoPeca(TipoPeca.NAO_METALICA)
            .orElseThrow(() -> new IllegalStateException(
                "O reservatório de peças não metálicas não foi configurado"
            ));

        boolean metalicoAtingiuCapacidade = metalico.adicionarPecas(request.quantidadeMetalicas());
        boolean naoMetalicoAtingiuCapacidade = naoMetalico.adicionarPecas(request.quantidadeNaoMetalicas());

        ContagemIntervalo contagem = new ContagemIntervalo(
            request.inicioIntervalo(),
            request.quantidadeMetalicas(),
            request.quantidadeNaoMetalicas()
        );

        contagemRepository.save(contagem);
        reservatorioRepository.save(metalico);
        reservatorioRepository.save(naoMetalico);

        return new ContagemIntervaloResponse(
            request.inicioIntervalo(),
            request.quantidadeMetalicas(),
            request.quantidadeNaoMetalicas(),
            metalicoAtingiuCapacidade,
            naoMetalicoAtingiuCapacidade
        );
    }

    @Transactional(readOnly = true) 
    public List<ContagemIntervaloHistoricoResponse> listarHistorico() {
        return contagemRepository.findAllByOrderByInicioIntervaloAsc()
            .stream()
            .map(contagem -> new ContagemIntervaloHistoricoResponse(
                contagem.getId(),
                contagem.getInicioIntervalo(),
                contagem.getQuantidadeMetalicas(),
                contagem.getQuantidadeNaoMetalicas()
            ))
            .toList();
    }
}
