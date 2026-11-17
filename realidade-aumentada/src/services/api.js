
const API_BASE = "/api/v1/analytics";

export function apiConfigurada() {
  return true;
}



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

function numeroOuNulo(valor) {
  return typeof valor === "number" &&
    Number.isFinite(valor) &&
    valor >= 0
    ? valor
    : null;
}

function prepararProducao(lista) {
  if (lista.length === 0) {
    return {
      totalPecas: null,
      pecasMetalicas: null,
      pecasNaoMetalicas: null,
    };
  }

  // Ordena pelo início do intervalo
  const registros = [...lista].sort((a, b) =>
    String(a?.inicioIntervalo ?? "").localeCompare(
      String(b?.inicioIntervalo ?? "")
    )
  );

  let metalicas = 0;
  let naoMetalicas = 0;

  for (const item of registros) {
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

  const ultimoRegistro =
    registros[registros.length - 1];

  const totalInformado = numeroOuNulo(
    ultimoRegistro?.totalPecas
  );

  return {
    totalPecas:
      totalInformado ?? metalicas + naoMetalicas,

    pecasMetalicas: metalicas,
    pecasNaoMetalicas: naoMetalicas,
  };
}

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

  // Só calcula quando os dois reservatórios
  // possuem informações válidas.
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

  const quantidade =
    qtdMetalico + qtdNaoMetalico;

  const capacidade =
    capMetalico + capNaoMetalico;

  // Alerta se qualquer reservatório
 
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

export async function buscarDados(signal) {
  const [producao, reservatorios] =
    await Promise.all([
      consultarLista("/production", signal),
      consultarLista("/reservoirs", signal),
    ]);

  return {
    ...prepararProducao(producao),

    reservatorio:
      prepararReservatorios(reservatorios),
  };
}
