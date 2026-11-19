import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Box } from "lucide-react";
import "../styles/GraficoProducao.css";

function GraficoReservatorio({ dados }) {
  const historico = Array.isArray(dados) ? dados : [];

  return (
    <section className="mt-card mt-grafico">
      <div className="mt-grafico-topo">
        <h3 className="mt-grafico-titulo">
          <Box size={22} />
          Evolução acumulada dos reservatórios
        </h3>
      </div>

      <div className="mt-barras-area">
        {historico.length === 0 ? (
          <div className="mt-histograma-vazio">Aguardando histórico de produção</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={historico} margin={{ top: 10, right: 12, left: -15, bottom: 0 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.08)" />
              <XAxis dataKey="hora" stroke="#cbd5e1" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} stroke="#cbd5e1" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  background: "#08131f",
                  border: "1px solid rgba(34, 224, 138, 0.3)",
                  borderRadius: "8px",
                  color: "#fff",
                }}
                formatter={(valor, nome) => [`${valor} peças`, nome]}
                labelFormatter={(hora) => `${hora} UTC`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="acumuladoMetalico"
                name="Reservatório metálico"
                stroke="#22e08a"
                strokeWidth={2.5}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="acumuladoNaoMetalico"
                name="Reservatório não metálico"
                stroke="#a78bfa"
                strokeWidth={2.5}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
      <p className="small text-secondary mb-0">
        Acumulado calculado pela soma das peças classificadas em cada minuto; valores em peças, não em percentual.
      </p>
    </section>
  );
}

export default GraficoReservatorio;
