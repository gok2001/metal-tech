package br.com.metaltech.monitoramento.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.OffsetDateTime;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

public record ContagemIntervaloRequest(

    @NotNull 
    @JsonProperty("inicio_intervalo") 
    OffsetDateTime inicioIntervalo,

    @NotNull 
    @PositiveOrZero 
    @JsonProperty("total_pecas") 
    Long totalPecas,

    @NotNull 
    @PositiveOrZero 
    @JsonProperty("quantidade_metalicas") 
    Integer quantidadeMetalicas,

    @NotNull 
    @PositiveOrZero 
    @JsonProperty("quantidade_nao_metalicas") 
    Integer quantidadeNaoMetalicas
) {

}
