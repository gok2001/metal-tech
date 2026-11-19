import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import { TrendingUp } from "lucide-react";
import "../styles/GraficoProducao.css";

var COR_METALICAS = "#2d8cff";
var COR_NAO_METALICAS = "#f59e0b";

// Converte o que chegar da API pro formato do gráfico.

function prepararDados(lista) {
  var resultado = [];
  if (!Array.isArray(lista)) {
    return resultado;
  }
  for (var i = 0; i < lista.length; i++) {
    var item = lista[i];
    resultado.push({
      hora: item.hora,
      metalicas: Number(item.metalicas) || 0,
      nao_metalicas: Number(item.nao_metalicas) || 0
    });
  }
  return resultado;
}

function GraficoProducao(props) {
  var dados = prepararDados(props.dados);

  // O histórico é apresentado cronologicamente como duas séries temporais.
  return (
    <section className="mt-card mt-grafico">
      <div className="mt-grafico-topo">
        <h3 className="mt-grafico-titulo">
          <TrendingUp size={30} />
          Evolução da Produção
        </h3>

        <div className="mt-legenda-linha">
          <span>
            <span className="mt-ponto" style={{ background: COR_METALICAS }}></span>
            Metálicas
          </span>
          <span>
            <span className="mt-ponto" style={{ background: COR_NAO_METALICAS }}></span>
            Não Metálicas
          </span>
        </div>
      </div>

      <div className="mt-barras-area">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={dados} margin={{ top: 10, right: 12, left: -15, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.08)" />
            <XAxis dataKey="hora" stroke="#cbd5e1" tick={{ fontSize: 12 }} />
            <YAxis
              stroke="#cbd5e1"
              tick={{ fontSize: 12 }}
              allowDecimals={false}
              domain={[0, "auto"]}
            />
            <Tooltip
              cursor={{ stroke: "rgba(255,255,255,0.18)", strokeDasharray: "3 3" }}
              contentStyle={{
                background: "#08131f",
                border: "1px solid rgba(34, 224, 138, 0.3)",
                borderRadius: "8px"
              }}
              labelStyle={{ color: "#e2e8f0" }}
            />
            <Line
              type="monotone"
              dataKey="metalicas"
              name="Metálicas"
              stroke={COR_METALICAS}
              strokeWidth={2.5}
              dot={{ r: 3, fill: COR_METALICAS }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="nao_metalicas"
              name="Não metálicas"
              stroke={COR_NAO_METALICAS}
              strokeWidth={2.5}
              dot={{ r: 3, fill: COR_NAO_METALICAS }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export default GraficoProducao;