package br.com.metaltech.monitoramento.dto.response;

import br.com.metaltech.monitoramento.enums.TipoPeca;

public record ReservatorioResponse(
    Long id,
    TipoPeca tipoPeca,
    Integer capacidadeMaxima,
    Integer quantidadeAtual,
    Integer ciclosCompletos
) {
    
}
