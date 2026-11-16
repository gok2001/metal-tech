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

    @Column(name = "total_pecas") 
    private Long totalPecas;

    @Column(name = "quantidade_metalicas", nullable = false) 
    private Integer quantidadeMetalicas;

    @Column(name = "quantidade_nao_metalicas", nullable = false) 
    private Integer quantidadeNaoMetalicas;

    protected ContagemIntervalo() {

    }

    public ContagemIntervalo(
        LocalDateTime inicioIntervalo,
        Long totalPecas,
        Integer quantidadeMetalicas,
        Integer quantidadeNaoMetalicas
    ) {
        this.inicioIntervalo = inicioIntervalo;
        this.totalPecas = totalPecas;
        this.quantidadeMetalicas = quantidadeMetalicas;
        this.quantidadeNaoMetalicas = quantidadeNaoMetalicas;
    }

    public Long getId() {
        return id;
    }

    public LocalDateTime getInicioIntervalo() {
        return inicioIntervalo;
    }

    public Long getTotalPecas() {
        return totalPecas;
    }

    public Integer getQuantidadeMetalicas() {
        return quantidadeMetalicas;
    }

    public Integer getQuantidadeNaoMetalicas() {
        return quantidadeNaoMetalicas;
    }
}
