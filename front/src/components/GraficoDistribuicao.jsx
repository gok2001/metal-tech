import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { PieChart as IconePizza } from "lucide-react";
import "../styles/GraficoDistribuicao.css";

var COR_METALICAS = "#2d8cff";
var COR_NAO_METALICAS = "#f59e0b";
var COR_VAZIO = "#1e293b";

function formatarPorcentagem(valor) {
  return valor.toFixed(1).replace(".", ",") + "%";
}

function GraficoDistribuicao(props) {
  var metalicas = props.metalicas || 0;
  var naoMetalicas = props.naoMetalicas || 0;
  var soma = metalicas + naoMetalicas;

  // protecao porcentagem em 0
  var pctMetalicas = 0;
  var pctNaoMetalicas = 0;
  if (soma > 0) {
    pctMetalicas = Math.round((metalicas / soma) * 1000) / 10;
    pctNaoMetalicas = Math.round((100 - pctMetalicas) * 10) / 10;
  }

  // dados do grafico desenhado
  var dadosGrafico = [
    { name: "Metálicas", value: metalicas },
    { name: "Não metálicas", value: naoMetalicas }
  ];
  var cores = [COR_METALICAS, COR_NAO_METALICAS];

  // sem as peças vai exibir a roda do grafico em cinza
  if (soma === 0) {
    dadosGrafico = [{ name: "Sem peças", value: 1 }];
    cores = [COR_VAZIO];
  }

  // puxa o valor de total para colocar no meio
  var total = props.total;
  if (total === undefined || total === null) {
    total = soma;
  }


  // Grafico feito com I.A
  
  return (
    <section className="mt-card mt-grafico">
      <h3 className="mt-grafico-titulo">
        <IconePizza size={22} />
        Distribuição de Peças
      </h3>
      <div className="mt-rosca-area">
        <div className="mt-rosca">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={dadosGrafico}
                dataKey="value"
                innerRadius="60%"
                outerRadius="100%"
                startAngle={90}
                endAngle={-270}
                stroke="none"
              >
                {dadosGrafico.map(function (item, i) {
                  return <Cell key={item.name} fill={cores[i]} />;
                })}
              </Pie>
            </PieChart>
          </ResponsiveContainer>

          <div className="mt-rosca-centro">
            <strong>{total.toLocaleString("pt-BR")}</strong>
            <small>Total</small>
          </div>
        </div>

        <div className="mt-legenda">
          <div className="mt-legenda-item">
            <span>
              <span className="mt-ponto" style={{ background: COR_METALICAS }}></span>
              Metálicas
            </span>
            <strong>{formatarPorcentagem(pctMetalicas)}</strong>
          </div>

          <div className="mt-legenda-item">
            <span>
              <span className="mt-ponto" style={{ background: COR_NAO_METALICAS }}></span>
              Não metálicas
            </span>
            <strong>{formatarPorcentagem(pctNaoMetalicas)}</strong>
          </div>
        </div>
      </div>
    </section>
  );
}

export default GraficoDistribuicao;