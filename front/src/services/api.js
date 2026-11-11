var API_URL = "";   // endereço do backend, não esquecer de colocar a api

export function buscarDados() {
  return fetch(API_URL + "/??") //não esquecer de colocar o endereço da api
    .then(function (resp) {
      if (!resp.ok) {
        throw new Error("Erro na API");
      }
      return resp.json();
    });
}