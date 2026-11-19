const API_ESTATISTICAS = "/api/stats/reservoirs";

function montarBoxplot(estatisticas) {
  if (!estatisticas) return null;

  const quartis = estatisticas.quartis || {};
  const valores = [
    estatisticas.minimo,
    quartis.q1,
    estatisticas.mediana,
    quartis.q3,
    estatisticas.maximo,
  ];

  const valido =
    valores.every((valor) => typeof valor === "number" && Number.isFinite(valor)) &&
    valores.every((valor, indice) => indice === 0 || valor >= valores[indice - 1]);

  if (!valido) return null;

  return {
    minimo: estatisticas.minimo,
    q1: quartis.q1,
    mediana: estatisticas.mediana,
    q3: quartis.q3,
    maximo: estatisticas.maximo,
  };
}

function prepararHistorico(lista) {
  if (!Array.isArray(lista)) return [];

  return lista
    .filter((item) => item && typeof item.timestamp === "string")
    .map((item) => ({
      hora: item.hora || item.timestamp.slice(11, 16),
      timestamp: item.timestamp,
      acumuladoMetalico: Number(item.acumuladoMetalico),
      acumuladoNaoMetalico: Number(item.acumuladoNaoMetalico),
    }))
    .filter((item) =>
      Number.isFinite(item.acumuladoMetalico) &&
      Number.isFinite(item.acumuladoNaoMetalico)
    );
}

function prepararHistograma(lista) {
  if (!Array.isArray(lista)) return [];

  return lista
    .filter((item) => item && Number.isFinite(Number(item.inicio)) && Number.isFinite(Number(item.fim)))
    .map((item) => ({
      inicio: Number(item.inicio),
      fim: Number(item.fim),
      intervalo: `${item.inicio}–${item.fim}`,
      frequenciaMetalica: Number(item.frequenciaMetalica) || 0,
      frequenciaNaoMetalica: Number(item.frequenciaNaoMetalica) || 0,
    }));
}

export async function buscarEstatisticasReservatorios() {
  const resposta = await fetch(API_ESTATISTICAS, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });

  if (!resposta.ok) {
    throw new Error(`Erro na API de estatísticas: HTTP ${resposta.status}`);
  }

  const dados = await resposta.json();
  const reservatorios = dados?.reservatorios;

  if (!reservatorios || typeof reservatorios !== "object" || Array.isArray(reservatorios)) {
    throw new Error("Formato inválido das estatísticas dos reservatórios");
  }

  const metalico = reservatorios.METALICA?.estatisticas ?? null;
  const naoMetalico = reservatorios.NAO_METALICA?.estatisticas ?? null;

  return {
    estatisticas_reservatorio_metalico: metalico,
    estatisticas_reservatorio_nao_metalico: naoMetalico,
    boxplot_reservatorio: {
      METALICA: montarBoxplot(metalico),
      NAO_METALICA: montarBoxplot(naoMetalico),
    },
    historico_reservatorio: prepararHistorico(dados.historicoReservatorios),
    histograma_reservatorio: prepararHistograma(dados.histogramaReservatorios),
    origem_dados_reservatorio: dados.origemDados || null,
    metodologia_reservatorio: dados.metodologia || null,
  };
}
