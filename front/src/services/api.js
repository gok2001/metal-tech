
const API_BASE = "/api/v1/analytics";

// end point

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

// validador

function numeroNaoNegativo(valor) {
  return typeof valor === "number" &&
    Number.isFinite(valor) &&
    valor >= 0
    ? valor
    : null;
}

// ==========================================
// CONVERTER DATA UTC
// ==========================================

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

// Estatísticas simples das quantidades observadas em cada minuto.
function calcularEstatisticasSerie(valores) {
  const serie = valores.filter((valor) => Number.isFinite(valor)).sort((a, b) => a - b);
  if (serie.length === 0) return null;
  const soma = serie.reduce((total, valor) => total + valor, 0);
  const media = soma / serie.length;
  const meio = Math.floor(serie.length / 2);
  const mediana = serie.length % 2 ? serie[meio] : (serie[meio - 1] + serie[meio]) / 2;
  const frequencias = new Map();
  serie.forEach((valor) => frequencias.set(valor, (frequencias.get(valor) || 0) + 1));
  const maiorFrequencia = Math.max(...frequencias.values());
  const moda = [...frequencias.entries()]
    .filter(([, frequencia]) => frequencia === maiorFrequencia)
    .map(([valor]) => valor);
  const variancia = serie.reduce((total, valor) => total + ((valor - media) ** 2), 0) / serie.length;
  const quantil = (q) => {
    const posicao = (serie.length - 1) * q;
    const inferior = Math.floor(posicao);
    const superior = Math.ceil(posicao);
    if (inferior === superior) return serie[inferior];
    return serie[inferior] + (serie[superior] - serie[inferior]) * (posicao - inferior);
  };
  return {
    quantidade: serie.length,
    media,
    mediana,
    moda,
    desvioPadrao: Math.sqrt(variancia),
    minimo: serie[0],
    maximo: serie[serie.length - 1],
    quartis: { q1: quantil(0.25), q2: mediana, q3: quantil(0.75) },
  };
}

// ==========================================
// PREPARAR DADOS DA PRODUÇÃO
// ==========================================

function prepararProducao(lista) {
  const registros = lista.map((item) => {
    const data = interpretarDataUtc(
      item?.inicioIntervalo
    );

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
    };
  });

  // Organiza os registros por horário
  registros.sort(
    (a, b) => a.data.getTime() - b.data.getTime()
  );

  // Sem leituras: não inventa valores
  if (registros.length === 0) {
    return {
      total_pecas: null,
      pecas_metalicas: null,
      pecas_nao_metalicas: null,
      historico_producao: [],
    };
  }

  // Soma todas as peças metálicas
  const totalMetalicas = registros.reduce(
    (soma, item) => soma + item.metalicas,
    0
  );

  // Soma todas as peças não metálicas
  const totalNaoMetalicas = registros.reduce(
    (soma, item) => soma + item.naoMetalicas,
    0
  );

  // CORREÇÃO: total geral é a soma das duas categorias
  
  const totalPecas =
    totalMetalicas + totalNaoMetalicas;

  return {
    total_pecas: totalPecas,

    pecas_metalicas: totalMetalicas,

    pecas_nao_metalicas: totalNaoMetalicas,

    historico_producao: registros.map((item) => ({
      hora: formatadorHora.format(item.data),
      metalicas: item.metalicas,
      nao_metalicas: item.naoMetalicas,
    })),
    estatisticas_producao: {
      metalicas: calcularEstatisticasSerie(registros.map((item) => item.metalicas)),
      naoMetalicas: calcularEstatisticasSerie(registros.map((item) => item.naoMetalicas)),
    },
  };
}

// prepara dados dash

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

// busca dados

export async function buscarDados() {
  try {

    // Consulta os dois endpoints
    const [producao, reservatorios] = await Promise.all([
      consultarLista("/production"),
      consultarLista("/reservoirs"),
    ]);

    // Prepara os dados para o Dashboard
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
