
const API_ESTATISTICAS = "/api/stats/reservoirs";

export async function buscarEstatisticasReservatorios() {
  const resposta = await fetch(API_ESTATISTICAS, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!resposta.ok) {
    throw new Error(
      `Erro na API de estatísticas: HTTP ${resposta.status}`
    );
  }

  const dados = await resposta.json();

  const reservatorios = dados?.reservatorios;

  if (
    !reservatorios ||
    typeof reservatorios !== "object" ||
    Array.isArray(reservatorios)
  ) {
    throw new Error("Formato inválido das estatísticas");
  }

  const encontrados = Object.entries(reservatorios).filter(
    ([, reservatorio]) => reservatorio?.estatisticas
  );

  // Evita combinar estatísticas de reservatórios
  // diferentes sem um cálculo apropriado.
  if (encontrados.length !== 1) {
    if (encontrados.length > 1) {
      console.warn(
        "Existem vários reservatórios. " +
        "É necessário definir a análise agregada."
      );
    }

    return {
      estatisticas_reservatorio: null,
      boxplot_reservatorio: null,
    };
  }

  const [tipo, reservatorio] = encontrados[0];

  const estatisticas = reservatorio.estatisticas;
  const quartis = estatisticas.quartis || {};

  const valoresBoxplot = [
    estatisticas.minimo,
    quartis.q1,
    estatisticas.mediana,
    quartis.q3,
    estatisticas.maximo,
  ];

  const boxplotValido =
    valoresBoxplot.every(Number.isFinite) &&
    valoresBoxplot.every(
      (valor, indice) =>
        indice === 0 || valor >= valoresBoxplot[indice - 1]
    );

  const boxplot = boxplotValido
    ? {
        minimo: estatisticas.minimo,
        q1: quartis.q1,
        mediana: estatisticas.mediana,
        q3: quartis.q3,
        maximo: estatisticas.maximo,
      }
    : null;

  console.log(
    `Estatísticas recebidas do reservatório ${tipo}`
  );

  return {
    estatisticas_reservatorio: estatisticas,
    boxplot_reservatorio: boxplot,
  };
}
