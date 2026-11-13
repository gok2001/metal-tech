import {
  BarChart,
  Bar,
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
// Se o back mandar com outros nomes de campo, é só mudar AQUI.
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

// cada item da lista: { hora: "08h", metalicas: 120, nao_metalicas: 80 }
function GraficoProducao(props) {
  var dados = props.dados || [];

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
          <BarChart data={dados} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.08)" />
            <XAxis dataKey="hora" stroke="#cbd5e1" tick={{ fontSize: 12 }} />
            <YAxis stroke="#cbd5e1" tick={{ fontSize: 12 }} />
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,0.05)" }}
              contentStyle={{
                background: "#08131f",
                border: "1px solid rgba(34, 224, 138, 0.3)",
                borderRadius: "8px"
              }}
            />
            <Bar dataKey="metalicas" name="Metálicas" fill={COR_METALICAS} radius={[4, 4, 0, 0]} />
            <Bar dataKey="nao_metalicas" name="Não metálicas" fill={COR_NAO_METALICAS} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export default GraficoProducao;