package br.com.metaltech.monitoramento.dto.request;

import java.time.LocalDateTime;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

public record ContagemIntervaloRequest(
    @NotNull 
    LocalDateTime inicioIntervalo,

    @NotNull 
    @PositiveOrZero 
    Integer quantidadeMetalicas,

    @NotNull 
    @PositiveOrZero 
    Integer quantidadeNaoMetalicas
) {

}
