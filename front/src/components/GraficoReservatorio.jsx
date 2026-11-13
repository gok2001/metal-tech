
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import { Box } from "lucide-react";
import "../styles/GraficoProducao.css";

var COR_RESERVATORIO = "#22e08a";

// Converte o que chegar da API pro formato do gráfico: { hora: "08h", quantidade: 20 }
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
      quantidade: Number(item.quantidade) || 0
    });
  }
  return resultado;
}

function GraficoReservatorio(props) {
  var dados = prepararDados(props.dados);

  return (
    <section className="mt-card mt-grafico">
      <div className="mt-grafico-topo">
        <h3 className="mt-grafico-titulo">
          <Box size={22} />
          Evolução do Reservatório
        </h3>

        <div className="mt-legenda-linha">
          <span>
            <span className="mt-ponto" style={{ background: COR_RESERVATORIO }}></span>
            Reservatório
          </span>
        </div>
      </div>

      <div className="mt-barras-area">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={dados} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="fundoReservatorio" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={COR_RESERVATORIO} stopOpacity={0.35} />
                <stop offset="100%" stopColor={COR_RESERVATORIO} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" />
            <XAxis dataKey="hora" stroke="#cbd5e1" tick={{ fontSize: 12 }} />
            <YAxis stroke="#cbd5e1" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                background: "#08131f",
                border: "1px solid rgba(34, 224, 138, 0.3)",
                borderRadius: "8px"
              }}
            />
            <Area
              type="linear"
              dataKey="quantidade"
              name="Reservatório"
              stroke={COR_RESERVATORIO}
              strokeWidth={3}
              fill="url(#fundoReservatorio)"
              dot={{ r: 4, fill: COR_RESERVATORIO, stroke: COR_RESERVATORIO }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export default GraficoReservatorio;