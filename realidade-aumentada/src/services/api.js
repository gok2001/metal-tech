
const API_URL = import.meta.env.VITE_API_MONITORAMENTO_URL?.trim();

export function apiConfigurada() {
  return Boolean(API_URL);
}

function numeroOuNulo(valor) {
  return typeof valor === "number" && Number.isFinite(valor)
    ? valor
    : null;
}

export async function buscarDados(signal) {
  if (!API_URL) {
    throw new Error("Endereço da API não configurado");
  }

  const resposta = await fetch(API_URL, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    signal,
    cache: "no-store",
  });

  if (!resposta.ok) {
    throw new Error(`Erro na API: ${resposta.status}`);
  }

  const dados = await resposta.json();

  if (!dados || typeof dados !== "object" || Array.isArray(dados)) {
    throw new Error("Formato de resposta inválido");
  }

  return {
    totalPecas: numeroOuNulo(dados.totalPecas),
    pecasMetalicas: numeroOuNulo(dados.pecasMetalicas),
    pecasNaoMetalicas: numeroOuNulo(dados.pecasNaoMetalicas),

    reservatorio: {
      quantidade: numeroOuNulo(dados.reservatorio?.quantidade),
      capacidade: numeroOuNulo(dados.reservatorio?.capacidade),
    },
  };
}
