
const API_URL = import.meta.env.VITE_API_URL || "";

export async function buscarDados() {
  // Enquanto o backend não estiver configurado,
  // informa que a API ainda não está disponível.
  if (!API_URL) {
    throw new Error("API ainda não configurada");
  }

  try {
    const resposta = await fetch(`${API_URL}/dados`, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      cache: "no-store",
    });

    if (!resposta.ok) {
      throw new Error(
        `Erro ao buscar dados: HTTP ${resposta.status}`
      );
    }

    const dados = await resposta.json();

    if (!dados || typeof dados !== "object" || Array.isArray(dados)) {
      throw new Error("Formato de resposta inválido");
    }

    return dados;
  } catch (erro) {
    console.error("MetalTech - Erro na API:", erro);
    throw erro;
  }
}
