package br.com.metaltech.monitoramento.dto.response;

import java.time.LocalDateTime;

public record ContagemIntervaloResponse(
    LocalDateTime inicioIntervalo,
    Integer quantidadeMetalicas,
    Integer quantidadeNaoMetalicas,
    boolean reservatorioMetalicoAtingiuCapacidade,
    boolean reservatorioNaoMetalicoAtingiuCapacidade
) {
    
}
