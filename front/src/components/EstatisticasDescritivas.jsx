import { ChartColumn } from "lucide-react";
import "../styles/EstatisticasDescritivas.css";

// número com 1 casa decimal e vírgula sem dado vira "-"
function formatarNumero(valor) {
  if (typeof valor !== "number" || !isFinite(valor)) {
    return "—";
  }
  return valor.toFixed(1).replace(".", ",");
}

// a moda chega como LISTA (pode ter vários valores ou nenhum)

function formatarModa(lista) {
  if (!Array.isArray(lista) || lista.length === 0) {
    return "—";
  }
  var textos = [];
  for (var i = 0; i < lista.length; i++) {
    textos.push(formatarNumero(lista[i]));
  }
  return textos.join(", ");
}

// transforma o objeto de estatísticas nas linhas que aparecem na tela.

function montarLinhas(estatisticas) {
  var e = estatisticas || {};
  var q = e.quartis || {};

  return [
    { nome: "Média", valor: formatarNumero(e.media) },
    { nome: "Mediana", valor: formatarNumero(e.mediana) },
    { nome: "Moda", valor: formatarModa(e.moda) },
    { nome: "Desvio Padrão", valor: formatarNumero(e.desvioPadrao) },
    { nome: "Q1", valor: formatarNumero(q.q1) + " | Q3: " + formatarNumero(q.q3) }
  ];
}

function EstatisticasDescritivas(props) {
  var colunas = [
    { titulo: "Peças Metálicas", cor: "#2d8cff", dados: props.metalicas },
    { titulo: "Peças Não Metálicas", cor: "#f59e0b", dados: props.naoMetalicas },
    { titulo: "Nível do Estoque", cor: "#22e08a", dados: props.estoque }
  ];

  return (
    <section className="mt-card mt-grafico mt-estatisticas">
      <h3 className="mt-grafico-titulo">
        <ChartColumn size={22} />
        Estatísticas Descritivas
      </h3>

      <div className="mt-est-colunas">
        {colunas.map(function (coluna) {
          var linhas = montarLinhas(coluna.dados);

          return (
            <div className="mt-est-coluna" key={coluna.titulo}>
              <div className="mt-est-titulo">
                <span className="mt-ponto" style={{ background: coluna.cor }}></span>
                {coluna.titulo}
              </div>

              {linhas.map(function (linha) {
                return (
                  <div className="mt-est-linha" key={linha.nome}>
                    <span>{linha.nome}:</span>
                    <strong>{linha.valor}</strong>
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default EstatisticasDescritivas;