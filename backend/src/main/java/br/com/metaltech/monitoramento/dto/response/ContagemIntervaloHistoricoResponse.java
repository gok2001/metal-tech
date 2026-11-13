package br.com.metaltech.monitoramento.dto.response;

import java.time.LocalDateTime;

public record ContagemIntervaloHistoricoResponse(
    Long id,
    LocalDateTime inicioIntervalo,
    Integer quantidadeMetalicas,
    Integer quantidadeNaoMetalicas
) {
    
}
