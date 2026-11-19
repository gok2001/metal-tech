import { BarChart3 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "../styles/HistogramaReservatorio.css";

function prepararDados(lista) {
  if (!Array.isArray(lista)) return [];
  return lista
    .filter((item) => item && Number.isFinite(Number(item.inicio)) && Number.isFinite(Number(item.fim)))
    .map((item) => ({
      intervalo: item.intervalo || `${item.inicio}–${item.fim}`,
      frequenciaMetalica: Number(item.frequenciaMetalica) || 0,
      frequenciaNaoMetalica: Number(item.frequenciaNaoMetalica) || 0,
    }));
}

export default function HistogramaReservatorio({ dados }) {
  const valores = prepararDados(dados);

  return (
    <section className="mt-card mt-caixa mt-histograma">
      <h3 className="mt-histograma-titulo">
        <BarChart3 size={20} color="#22e08a" />
        Histograma dos acumulados
      </h3>
      <div className="mt-histograma-area">
        {valores.length === 0 ? (
          <div className="mt-histograma-vazio">Aguardando histórico de produção</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={valores} margin={{ top: 10, right: 10, left: -15, bottom: 5 }}>
              <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.08)" />
              <XAxis dataKey="intervalo" stroke="#94a3b8" tick={{ fontSize: 10 }} />
              <YAxis allowDecimals={false} stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#08131f", border: "1px solid #22e08a", borderRadius: "8px", color: "#fff" }}
                formatter={(valor, nome) => [valor, nome]}
              />
              <Legend />
              <Bar dataKey="frequenciaMetalica" name="Acumulado metálico" fill="#22e08a" />
              <Bar dataKey="frequenciaNaoMetalica" name="Acumulado não metálico" fill="#a78bfa" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
      <p className="small text-secondary mb-0">
        Frequência dos valores acumulados observados nos 21 intervalos de produção.
      </p>
    </section>
  );
}
