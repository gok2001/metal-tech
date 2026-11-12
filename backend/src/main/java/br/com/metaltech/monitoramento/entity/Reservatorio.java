package br.com.metaltech.monitoramento.entity;

import br.com.metaltech.monitoramento.enums.TipoPeca;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity 
@Table(name = "reservatorio") 
public class Reservatorio {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY) 
    private Long id;

    @Enumerated(EnumType.STRING) 
    @Column(name = "tipo_peca", nullable = false, unique = true, length = 20) 
    private TipoPeca tipoPeca;

    @Column(name = "capacidade_maxima", nullable = false) 
    private Integer capacidadeMaxima;

    @Column(name = "quantidade_atual", nullable = false) 
    private Integer quantidadeAtual;

    @Column(name = "ciclos_completos", nullable = false) 
    private Integer ciclosCompletos;

    protected Reservatorio() {

    }

    public Long getId() {
        return id;
    }

    public TipoPeca getTipoPeca() {
        return tipoPeca;
    }

    public Integer getCapacidadeMaxima() {
        return capacidadeMaxima;
    }

    public Integer getQuantidadeAtual() {
        return quantidadeAtual;
    }

    public Integer getCiclosCompletos() {
        return ciclosCompletos;
    }

    public boolean adicionarPecas(int quantidade) {
        if (quantidade < 0) {
            throw new IllegalArgumentException("A quantidade de peças não pode ser negativa");
        }

        if (capacidadeMaxima == null || capacidadeMaxima <= 0) {
            throw new IllegalArgumentException("A capacidade do reservatório precisa ser maior que zero");
        }

        if (quantidadeAtual == null || ciclosCompletos == null) {
            throw new IllegalArgumentException("O reservatório precisa ser inicializado");
        }

        boolean atingiuCapacidade = false;

        for (int i = 0; i < quantidade; i++) {
            if (quantidadeAtual.intValue() == capacidadeMaxima.intValue()) {
                quantidadeAtual = 0;
            }

            quantidadeAtual++;

            if (quantidadeAtual.intValue() == capacidadeMaxima.intValue()) {
                ciclosCompletos++;
                atingiuCapacidade = true;
            }
        }

        return atingiuCapacidade;
    }
}
