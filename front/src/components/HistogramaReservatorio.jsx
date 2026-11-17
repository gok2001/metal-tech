
import { BarChart3 } from "lucide-react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import "../styles/HistogramaReservatorio.css";

// prepara os intervalos recebidos da API
function prepararDados(lista) {
  if (!Array.isArray(lista)) return [];

  return lista
    .filter(
      (item) =>
        item &&
        item.inicio != null &&
        item.fim != null &&
        item.frequencia != null
    )
    .map((item) => ({
      inicio: Number(item.inicio),
      fim: Number(item.fim),
      frequencia: Number(item.frequencia),
    }))
    .filter(
      (item) =>
        Number.isFinite(item.inicio) &&
        Number.isFinite(item.fim) &&
        Number.isInteger(item.frequencia) &&
        item.fim > item.inicio &&
        item.frequencia >= 0
    )
    .sort((a, b) => a.inicio - b.inicio)
    .map((item) => ({
      ...item,
      intervalo: `${item.inicio}–${item.fim}`,
    }));
}

export default function HistogramaReservatorio({ dados }) {
  const valores = prepararDados(dados);

  return (
    <section className="mt-card mt-caixa mt-histograma">

      <h3 className="mt-histograma-titulo">
        <BarChart3 size={20} color="#22e08a" />
        Histograma Reservatório
      </h3>

      <div className="mt-histograma-area">
        {valores.length === 0 ? (
          <div className="mt-histograma-vazio">
            Aguardando dados do reservatório
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={valores}
              barCategoryGap="0%"
              margin={{
                top: 10,
                right: 10,
                left: -15,
                bottom: 5,
              }}
            >
              <CartesianGrid
                vertical={false}
                stroke="rgba(255,255,255,0.08)"
              />

              <XAxis
                dataKey="intervalo"
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
              />

              <YAxis
                allowDecimals={false}
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
              />

              <Tooltip
                contentStyle={{
                  background: "#08131f",
                  border: "1px solid #22e08a",
                  borderRadius: "8px",
                  color: "#fff",
                }}
                formatter={(valor) => [valor, "Frequência"]}
              />

              <Bar
                dataKey="frequencia"
                fill="#22e08a"
                stroke="#050c14"
                strokeWidth={1}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

    </section>
  );
}
