
const API_BASE = "/api/v1/analytics";

// Consulta um endpoint que retorna uma lista
async function consultarLista(caminho) {
  const resposta = await fetch(`${API_BASE}${caminho}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!resposta.ok) {
    throw new Error(
      `Erro na API (${caminho}): HTTP ${resposta.status}`
    );
  }

  const dados = await resposta.json();

  if (!Array.isArray(dados)) {
    throw new Error(
      `Resposta inesperada da API (${caminho})`
    );
  }

  return dados;
}

// Aceita apenas números válidos
function numeroNaoNegativo(valor) {
  return typeof valor === "number" &&
    Number.isFinite(valor) &&
    valor >= 0
    ? valor
    : null;
}

// Converte a data UTC do Back-End
function interpretarDataUtc(valor) {
  if (typeof valor !== "string" || !valor) {
    return null;
  }

  const temFuso = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(valor);

  const data = new Date(
    temFuso ? valor : `${valor}Z`
  );

  return Number.isNaN(data.getTime()) ? null : data;
}

const formatadorHora = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

// Prepara os dados da produção
function prepararProducao(lista) {
  const registros = lista.map((item) => {
    const data = interpretarDataUtc(item?.inicioIntervalo);

    const metalicas = numeroNaoNegativo(
      item?.quantidadeMetalicas
    );

    const naoMetalicas = numeroNaoNegativo(
      item?.quantidadeNaoMetalicas
    );

    if (
      !data ||
      metalicas === null ||
      naoMetalicas === null
    ) {
      throw new Error(
        "Histórico da produção contém um registro inválido"
      );
    }

    return {
      data,
      metalicas,
      naoMetalicas,
      totalAcumulado: numeroNaoNegativo(item.totalPecas),
    };
  });

  // Organiza pelo horário
  registros.sort(
    (a, b) => a.data.getTime() - b.data.getTime()
  );

  // Ainda não existem leituras
  if (registros.length === 0) {
    return {
      total_pecas: null,
      pecas_metalicas: null,
      pecas_nao_metalicas: null,
      historico_producao: [],
    };
  }

  // Soma as contagens dos intervalos
  const totalMetalicas = registros.reduce(
    (soma, item) => soma + item.metalicas,
    0
  );

  const totalNaoMetalicas = registros.reduce(
    (soma, item) => soma + item.naoMetalicas,
    0
  );

  // Utiliza o último total acumulado informado
  // pelo Back-End, quando disponível.
  const totalAcumulado =
    registros[registros.length - 1].totalAcumulado;

  return {
    total_pecas:
      totalAcumulado ?? totalMetalicas + totalNaoMetalicas,

    pecas_metalicas: totalMetalicas,

    pecas_nao_metalicas: totalNaoMetalicas,

    historico_producao: registros.map((item) => ({
      hora: formatadorHora.format(item.data),
      metalicas: item.metalicas,
      nao_metalicas: item.naoMetalicas,
    })),
  };
}

// Prepara os dados dos reservatórios
function prepararReservatorios(lista) {
  const metalico = lista.find(
    (item) => item?.tipoPeca === "METALICA"
  );

  const naoMetalico = lista.find(
    (item) => item?.tipoPeca === "NAO_METALICA"
  );

  return {
    quantidade_reservatorio_metalico:
      numeroNaoNegativo(metalico?.quantidadeAtual),

    capacidade_reservatorio_metalico:
      numeroNaoNegativo(metalico?.capacidadeMaxima),

    quantidade_reservatorio_nao_metalico:
      numeroNaoNegativo(naoMetalico?.quantidadeAtual),

    capacidade_reservatorio_nao_metalico:
      numeroNaoNegativo(naoMetalico?.capacidadeMaxima),
  };
}

// Função utilizada pelo Dashboard.jsx
export async function buscarDados() {
  try {
    // Consulta os dois endpoints
    const [producao, reservatorios] = await Promise.all([
      consultarLista("/production"),
      consultarLista("/reservoirs"),
    ]);

    // Entrega os dados no formato do Front-End
    return {
      ...prepararProducao(producao),
      ...prepararReservatorios(reservatorios),

      ultima_atualizacao: new Date(),
    };
  } catch (erro) {
    console.error(
      "MetalTech - Erro ao consultar o Back-End:",
      erro
    );

    throw erro;
  }
}
