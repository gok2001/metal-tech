package br.com.metaltech.monitoramento.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity 
@Table(name = "contagem_intervalo") 
public class ContagemIntervalo {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY) 
    private Long id;

    @Column(name = "inicio_intervalo", nullable = false, unique = true) 
    private LocalDateTime inicioIntervalo;

    @Column(name = "quantidade_metalicas", nullable = false) 
    private Integer quantidadeMetalicas;

    @Column(name = "quantidade_nao_metalicas", nullable = false) 
    private Integer quantidadeNaoMetalicas;

    protected ContagemIntervalo() {

    }

    public ContagemIntervalo(
        LocalDateTime inicioIntervalo,
        Integer quantidadeMetalicas,
        Integer quantidadeNaoMetalicas
    ) {
        this.inicioIntervalo = inicioIntervalo;
        this.quantidadeMetalicas = quantidadeMetalicas;
        this.quantidadeNaoMetalicas = quantidadeNaoMetalicas;
    }
}
