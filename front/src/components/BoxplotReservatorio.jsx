import { BarChart3 } from "lucide-react";
import "../styles/BoxplotReservatorio.css";

function validarBoxplot(dados) {
  if (!dados || typeof dados !== "object") return null;

  const campos = ["minimo", "q1", "mediana", "q3", "maximo"];
  if (campos.some((campo) => dados[campo] == null || dados[campo] === "")) {
    return null;
  }

  const valores = campos.map((campo) => Number(dados[campo]));
  if (!valores.every(Number.isFinite)) return null;

  const [minimo, q1, mediana, q3, maximo] = valores;
  if (minimo > q1 || q1 > mediana || mediana > q3 || q3 > maximo) return null;

  return { minimo, q1, mediana, q3, maximo };
}

function BoxplotIndividual({ titulo, dados }) {
  const valores = validarBoxplot(dados);
  const formatar = (valor) =>
    new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 }).format(valor);

  function posicao(valor) {
    if (valores.maximo === valores.minimo) return 150;
    return 30 + ((valor - valores.minimo) / (valores.maximo - valores.minimo)) * 240;
  }

  return (
    <div className="mt-boxplot-individual">
      <h4 className="mt-boxplot-subtitulo">{titulo}</h4>
      {!valores ? (
        <div className="mt-boxplot-vazio">Aguardando dados</div>
      ) : (
        <>
          <svg viewBox="0 0 300 130" className="mt-boxplot-svg" role="img" aria-label={`Boxplot ${titulo}`}>
            <line x1={posicao(valores.minimo)} y1="60" x2={posicao(valores.maximo)} y2="60" stroke="#94a3b8" strokeWidth="2" />
            <line x1={posicao(valores.minimo)} y1="40" x2={posicao(valores.minimo)} y2="80" stroke="#22e08a" strokeWidth="2" />
            <line x1={posicao(valores.maximo)} y1="40" x2={posicao(valores.maximo)} y2="80" stroke="#22e08a" strokeWidth="2" />
            <rect x={posicao(valores.q1)} y="30" width={Math.max(0, posicao(valores.q3) - posicao(valores.q1))} height="60" fill="rgba(34,224,138,0.20)" stroke="#22e08a" strokeWidth="2" rx="3" />
            <line x1={posicao(valores.mediana)} y1="30" x2={posicao(valores.mediana)} y2="90" stroke="#00bfff" strokeWidth="3" />
            <text x="30" y="115" fill="#94a3b8" fontSize="10">{formatar(valores.minimo)}</text>
            <text x="270" y="115" textAnchor="end" fill="#94a3b8" fontSize="10">{formatar(valores.maximo)}</text>
          </svg>
          <div className="mt-boxplot-legenda">
            <div><span>Mínimo</span><strong>{formatar(valores.minimo)}</strong></div>
            <div><span>Q1</span><strong>{formatar(valores.q1)}</strong></div>
            <div><span>Mediana</span><strong>{formatar(valores.mediana)}</strong></div>
            <div><span>Q3</span><strong>{formatar(valores.q3)}</strong></div>
            <div><span>Máximo</span><strong>{formatar(valores.maximo)}</strong></div>
          </div>
        </>
      )}
    </div>
  );
}

export default function BoxplotReservatorio({ dados }) {
  return (
    <section className="mt-card mt-caixa mt-boxplot">
      <h3 className="mt-boxplot-titulo">
        <BarChart3 size={20} color="#22e08a" />
        Boxplot dos Reservatórios
      </h3>
      <div className="mt-boxplot-comparativo">
        <BoxplotIndividual titulo="Reservatório metálico" dados={dados?.METALICA} />
        <BoxplotIndividual titulo="Reservatório não metálico" dados={dados?.NAO_METALICA} />
      </div>
    </section>
  );
}
