package br.com.metaltech.monitoramento.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.LocalDateTime;

public record AnomaliaResponse(
    Long id,

    @JsonProperty("id_origem") 
    String idOrigem,

    String tipo,
    String equipamento,

    @JsonProperty("tipo_reservatorio") 
    String tipoReservatorio,

    String descricao,
    String severidade,

    @JsonProperty("data_ocorrencia") 
    LocalDateTime dataOcorrencia
) {
    
}
