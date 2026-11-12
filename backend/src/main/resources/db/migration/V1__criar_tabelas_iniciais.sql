CREATE TABLE reservatorio (
    id BIGINT NOT NULL AUTO_INCREMENT,
    tipo_peca VARCHAR(20) NOT NULL,
    capacidade_maxima INT NOT NULL,
    quantidade_atual INT NOT NULL DEFAULT 0,
    ciclos_completos INT NOT NULL DEFAULT 0,

    PRIMARY KEY (id),
    CONSTRAINT uq_reservatorio_tipo_peca UNIQUE (tipo_peca),
    CONSTRAINT chk_reservatorio_capacidade CHECK (capacidade_maxima > 0),
    CONSTRAINT chk_reservatorio_quantidade CHECK (quantidade_atual >= 0),
    CONSTRAINT chk_reservatorio_ciclos CHECK (ciclos_completos >= 0)
);

CREATE TABLE contagem_intervalo (
    id BIGINT NOT NULL AUTO_INCREMENT,
    inicio_intervalo DATETIME NOT NULL,
    quantidade_metalicas INT NOT NULL,
    quantidade_nao_metalicas INT NOT NULL,

    PRIMARY KEY (id),
    CONSTRAINT uq_contagem_intervalo_inicio UNIQUE (inicio_intervalo),
    CONSTRAINT chk_contagem_metalicas CHECK (quantidade_metalicas >= 0),
    CONSTRAINT chk_contagem_nao_metalicas CHECK (quantidade_nao_metalicas >= 0)
);