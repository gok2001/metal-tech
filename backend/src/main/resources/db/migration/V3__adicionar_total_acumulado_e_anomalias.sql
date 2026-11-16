ALTER TABLE contagem_intervalo
    ADD COLUMN total_pecas BIGINT NULL,
    ADD CONSTRAINT chk_contagem_intervalo_total_pecas
        CHECK (total_pecas IS NULL OR total_pecas >= 0);

CREATE TABLE anomalia (
    id BIGINT NOT NULL AUTO_INCREMENT,
    id_origem VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    equipamento VARCHAR(100) NOT NULL,
    tipo_reservatorio VARCHAR(20) NOT NULL,
    descricao TEXT NOT NULL,
    severidade VARCHAR(20) NOT NULL,
    data_ocorrencia DATETIME NOT NULL,

    PRIMARY KEY (id),
    CONSTRAINT uq_anomalia_origem
        UNIQUE (equipamento, id_origem),
    CONSTRAINT chk_anomalia_tipo_reservatorio
        CHECK (tipo_reservatorio IN ('METALICA', 'NAO_METALICA'))
);