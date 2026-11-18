import { ChartColumn } from "lucide-react";
import "../styles/EstatisticasDescritivas.css";

function formatarNumero(valor) {
  if (typeof valor !== "number" || !Number.isFinite(valor)) return "—";
  return valor.toFixed(1).replace(".", ",");
}

function formatarModa(lista) {
  if (!Array.isArray(lista) || lista.length === 0) return "—";
  return lista.map(formatarNumero).join(", ");
}

function montarLinhas(estatisticas) {
  const e = estatisticas || {};
  const q = e.quartis || {};

  return [
    { nome: "Média", valor: formatarNumero(e.media) },
    { nome: "Mediana", valor: formatarNumero(e.mediana) },
    { nome: "Moda", valor: formatarModa(e.moda) },
    { nome: "Desvio padrão", valor: formatarNumero(e.desvioPadrao) },
    { nome: "Q1 / Q3", valor: `${formatarNumero(q.q1)} / ${formatarNumero(q.q3)}` },
  ];
}

export default function EstatisticasDescritivas(props) {
  const colunas = [
    { titulo: "Peças metálicas", cor: "#2d8cff", dados: props.metalicas },
    { titulo: "Peças não metálicas", cor: "#f59e0b", dados: props.naoMetalicas },
    { titulo: "Reservatório metálico", cor: "#22e08a", dados: props.estoqueMetalico },
    { titulo: "Reservatório não metálico", cor: "#a78bfa", dados: props.estoqueNaoMetalico },
  ];

  return (
    <section className="mt-card mt-grafico mt-estatisticas">
      <h3 className="mt-grafico-titulo">
        <ChartColumn size={22} />
        Estatísticas Descritivas
      </h3>

      <div className="mt-est-colunas">
        {colunas.map((coluna) => (
          <div className="mt-est-coluna" key={coluna.titulo}>
            <div className="mt-est-titulo">
              <span className="mt-ponto" style={{ background: coluna.cor }} />
              {coluna.titulo}
            </div>

            {montarLinhas(coluna.dados).map((linha) => (
              <div className="mt-est-linha" key={linha.nome}>
                <span>{linha.nome}:</span>
                <strong>{linha.valor}</strong>
              </div>
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}
