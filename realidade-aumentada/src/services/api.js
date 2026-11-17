
const API_BASE = "/api/v1/analytics";

// ==========================================
// VERIFICAR CONFIGURAÇÃO DA API
// ==========================================

export function apiConfigurada() {
  return true;
}

// ==========================================
// CONSULTAR ENDPOINTS DO BACKEND
// ==========================================

async function consultarLista(rota, signal) {
  const resposta = await fetch(
    `${API_BASE}${rota}`,
    {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      signal,
      cache: "no-store",
    }
  );

  if (!resposta.ok) {
    throw new Error(
      `Erro na API (${rota}): HTTP ${resposta.status}`
    );
  }

  const dados = await resposta.json();

  if (!Array.isArray(dados)) {
    throw new Error(
      `Resposta inválida da API: ${rota}`
    );
  }

  return dados;
}

// ==========================================
// VALIDAR VALORES NUMÉRICOS
// ==========================================

function numeroOuNulo(valor) {
  return typeof valor === "number" &&
    Number.isFinite(valor) &&
    valor >= 0
    ? valor
    : null;
}

// ==========================================
// PREPARAR DADOS DA PRODUÇÃO
// ==========================================

function prepararProducao(lista) {
  // Sem registros, não apresenta valores fictícios
  if (lista.length === 0) {
    return {
      totalPecas: null,
      pecasMetalicas: null,
      pecasNaoMetalicas: null,
    };
  }

  let metalicas = 0;
  let naoMetalicas = 0;

  // Soma as contagens de todos os intervalos
  for (const item of lista) {
    const qtdMetalicas = numeroOuNulo(
      item?.quantidadeMetalicas
    );

    const qtdNaoMetalicas = numeroOuNulo(
      item?.quantidadeNaoMetalicas
    );

    if (
      qtdMetalicas === null ||
      qtdNaoMetalicas === null
    ) {
      throw new Error(
        "O backend retornou contagens inválidas"
      );
    }

    metalicas += qtdMetalicas;
    naoMetalicas += qtdNaoMetalicas;
  }

  // CORREÇÃO:
  // Total geral = metálicas + não metálicas
  const totalPecas = metalicas + naoMetalicas;

  return {
    totalPecas: totalPecas,
    pecasMetalicas: metalicas,
    pecasNaoMetalicas: naoMetalicas,
  };
}

// ==========================================
// PREPARAR DADOS DOS RESERVATÓRIOS
// ==========================================

function prepararReservatorios(lista) {
  const metalico = lista.find(
    (item) => item?.tipoPeca === "METALICA"
  );

  const naoMetalico = lista.find(
    (item) => item?.tipoPeca === "NAO_METALICA"
  );

  const qtdMetalico = numeroOuNulo(
    metalico?.quantidadeAtual
  );

  const capMetalico = numeroOuNulo(
    metalico?.capacidadeMaxima
  );

  const qtdNaoMetalico = numeroOuNulo(
    naoMetalico?.quantidadeAtual
  );

  const capNaoMetalico = numeroOuNulo(
    naoMetalico?.capacidadeMaxima
  );

  // Verifica se os dois reservatórios
  // possuem dados válidos
  const completo = [
    qtdMetalico,
    capMetalico,
    qtdNaoMetalico,
    capNaoMetalico,
  ].every((valor) => valor !== null);

  if (!completo) {
    return {
      quantidade: null,
      capacidade: null,
      alerta: false,
    };
  }

  // Soma as quantidades dos dois reservatórios
  const quantidade =
    qtdMetalico + qtdNaoMetalico;

  // Soma as capacidades dos dois reservatórios
  const capacidade =
    capMetalico + capNaoMetalico;

  // Alerta se qualquer reservatório
  // atingir 80% da própria capacidade
  const alerta =
    (capMetalico > 0 &&
      qtdMetalico / capMetalico >= 0.8) ||
    (capNaoMetalico > 0 &&
      qtdNaoMetalico / capNaoMetalico >= 0.8);

  return {
    quantidade,
    capacidade,
    alerta,
  };
}

// ==========================================
// BUSCAR DADOS REAIS DO BACKEND
// ==========================================

export async function buscarDados(signal) {
  // Consulta os dois endpoints
  const [producao, reservatorios] =
    await Promise.all([
      consultarLista("/production", signal),
      consultarLista("/reservoirs", signal),
    ]);

  // Retorna os dados no formato
  // utilizado pelos cards da RA
  return {
    ...prepararProducao(producao),

    reservatorio:
      prepararReservatorios(reservatorios),
  };
}
