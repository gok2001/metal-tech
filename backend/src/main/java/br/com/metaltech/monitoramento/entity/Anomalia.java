package br.com.metaltech.monitoramento.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;

@Entity 
@Table(
    name = "anomalia",
    uniqueConstraints = @UniqueConstraint(
        name = "uq_anomalia_origem",
        columnNames = {"equipamento", "id_origem"}
    )
) 
public class Anomalia {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY) 
    private Long id;

    @Column(name = "id_origem", nullable = false, length = 100) 
    private String idOrigem;

    @Column(nullable = false, length = 50) 
    private String tipo;

    @Column(nullable = false, length = 100) 
    private String equipamento;

    @Column(name = "tipo_reservatorio", nullable = false, length = 20) 
    private String tipoReservatorio;

    @Column(nullable = false, columnDefinition = "TEXT") 
    private String descricao;

    @Column(nullable = false, length = 20) 
    private String severidade;

    @Column(name = "data_ocorrencia", nullable = false) 
    private LocalDateTime dataOcorrencia;

    protected Anomalia() {

    }

    public Anomalia(
        String idOrigem,
        String tipo,
        String equipamento,
        String tipoReservatorio,
        String descricao,
        String severidade,
        LocalDateTime dataOcorrencia
    ) {
        this.idOrigem = idOrigem;
        this.tipo = tipo;
        this.equipamento = equipamento;
        this.tipoReservatorio = tipoReservatorio;
        this.descricao = descricao;
        this.severidade = severidade;
        this.dataOcorrencia = dataOcorrencia;
    }
}
