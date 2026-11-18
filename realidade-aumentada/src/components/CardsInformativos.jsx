
import { Layers3, Cog, Package, Box } from "lucide-react";

export default function CardsInformativos({ dados }) {
  const total = dados?.totalPecas;
  const metalicas = dados?.pecasMetalicas;
  const naoMetalicas = dados?.pecasNaoMetalicas;

  const quantidade = dados?.reservatorio?.quantidade;
  const capacidade = dados?.reservatorio?.capacidade;

  const temOcupacao =
    Number.isFinite(quantidade) &&
    Number.isFinite(capacidade) &&
    capacidade > 0;

  const ocupacao = temOcupacao
    ? Math.min(100, Math.max(0, (quantidade / capacidade) * 100))
    : null;

  function formatar(valor) {
    return Number.isFinite(valor)
      ? valor.toLocaleString("pt-BR")
      : "—";
  }

  return (
    <div className="cards-informativos">
      <div className="indicadores-superiores">

        {/* Total de peças - Verde */}
        <div className="indicador-card verde">
          <h3 className="indicador-titulo">
            <Layers3 className="icone-indicador" />
            <span>Total de peças</span>
          </h3>
          <strong>{formatar(total)}</strong>
        </div>

        {/* Peças metálicas - Azul */}
        <div className="indicador-card azul">
          <h3 className="indicador-titulo">
            <Cog className="icone-indicador" />
            <span>Peças metálicas</span>
          </h3>
          <strong>{formatar(metalicas)}</strong>
        </div>

        {/* Peças não metálicas - Amarelo */}
        <div className="indicador-card amarelo">
          <h3 className="indicador-titulo">
            <Package className="icone-indicador" />
            <span>Peças não metálicas</span>
          </h3>
          <strong>{formatar(naoMetalicas)}</strong>
        </div>

      </div>

      {/* Ocupação do reservatório */}
      <div className="reservatorio-card hud-card">
        <h3 className="reservatorio-titulo">
          <Box className="icone-reservatorio" />
          <span>Ocupação do reservatório</span>
        </h3>

        <strong className="ocupacao-valor">
          {ocupacao === null
            ? "—"
            : `${Math.round(ocupacao)}%`}
        </strong>

        <div className="barra-ocupacao">
          <div
            className="barra-preenchimento"
            style={{ width: `${ocupacao ?? 0}%` }}
          />

          <span className="barra-texto">
            {formatar(quantidade)} / {formatar(capacidade)} peças
          </span>
        </div>

        {ocupacao !== null && ocupacao >= 80 && (
          <p className="alerta-reservatorio">
            ⚠ Reservatório próximo da capacidade máxima!
          </p>
        )}
      </div>
    </div>
  );
}
