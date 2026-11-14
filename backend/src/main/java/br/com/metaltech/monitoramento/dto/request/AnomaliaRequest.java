package br.com.metaltech.monitoramento.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.OffsetDateTime;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

public record AnomaliaRequest(
    @NotBlank 
    @JsonProperty("id") 
    String idOrigem,

    @NotBlank 
    String tipo,

    @NotBlank 
    String equipamento,

    @NotBlank 
    @Pattern(regexp = "METALICA|NAO_METALICA") 
    @JsonProperty("tipo_reservatorio")
    String tipoReservatorio,

    @NotBlank 
    String descricao,

    @NotBlank 
    String severidade,

    @NotNull 
    @JsonProperty("data_ocorrencia") 
    OffsetDateTime dataOcorrencia
) {
    
}
