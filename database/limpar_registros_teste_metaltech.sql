USE metaltech;

-- Mantém exclusivamente as 21 consolidações do histórico oficial de 258 eventos.
-- A tabela `reservatorio` NÃO é alterada por este script.
START TRANSACTION;

CREATE TEMPORARY TABLE tmp_intervalos_oficiais (
    inicio_intervalo DATETIME NOT NULL PRIMARY KEY
);

INSERT INTO tmp_intervalos_oficiais (inicio_intervalo) VALUES
('2026-11-18 00:54:00'),
('2026-11-18 00:55:00'),
('2026-11-18 00:56:00'),
('2026-11-18 00:57:00'),
('2026-11-18 00:58:00'),
('2026-11-18 01:06:00'),
('2026-11-18 01:07:00'),
('2026-11-18 01:08:00'),
('2026-11-18 01:09:00'),
('2026-11-18 01:10:00'),
('2026-11-18 01:13:00'),
('2026-11-18 01:14:00'),
('2026-11-18 01:15:00'),
('2026-11-18 01:16:00'),
('2026-11-18 01:18:00'),
('2026-11-18 01:19:00'),
('2026-11-18 01:22:00'),
('2026-11-18 01:23:00'),
('2026-11-18 01:25:00'),
('2026-11-18 01:31:00'),
('2026-11-18 01:32:00');

SET @oficiais_encontrados = (
    SELECT COUNT(DISTINCT c.inicio_intervalo)
    FROM contagem_intervalo c
    INNER JOIN tmp_intervalos_oficiais o
        ON o.inicio_intervalo = c.inicio_intervalo
);

SELECT
    @oficiais_encontrados AS intervalos_oficiais_confirmados,
    (SELECT COUNT(*) FROM contagem_intervalo) AS intervalos_antes_limpeza,
    (SELECT COUNT(*) FROM anomalia) AS anomalias_antes_limpeza;

-- A limpeza só ocorre se os 21 intervalos oficiais estiverem presentes.
DELETE FROM contagem_intervalo
WHERE @oficiais_encontrados = 21
  AND inicio_intervalo NOT IN (
      SELECT inicio_intervalo FROM tmp_intervalos_oficiais
  );

-- O histórico oficial contém zero inconsistências; remove a anomalia antiga de teste.
DELETE FROM anomalia
WHERE @oficiais_encontrados = 21;

SELECT
    COUNT(*) AS intervalos_finais,
    SUM(total_pecas) AS total_pecas,
    SUM(quantidade_metalicas) AS pecas_metalicas,
    SUM(quantidade_nao_metalicas) AS pecas_nao_metalicas
FROM contagem_intervalo;

SELECT COUNT(*) AS anomalias_finais FROM anomalia;

-- IMPORTANTE: nenhuma instrução altera tabela `reservatorio`.
DROP TEMPORARY TABLE tmp_intervalos_oficiais;
COMMIT;
