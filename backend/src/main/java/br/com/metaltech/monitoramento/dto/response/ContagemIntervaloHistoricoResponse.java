package br.com.metaltech.monitoramento.dto.response;

import java.time.LocalDateTime;

public record ContagemIntervaloHistoricoResponse(
    Long id,
    LocalDateTime inicioIntervalo,
    Long totalPecas,
    Integer quantidadeMetalicas,
    Integer quantidadeNaoMetalicas
) {
    
}
