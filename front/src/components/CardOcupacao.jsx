
import "../styles/CardOcupacao.css";

function CardOcupacao({ titulo, percentual, icone, cor = "azul" }) {
  const valorValido =
    typeof percentual === "number" &&
    Number.isFinite(percentual);

  const ocupacao = valorValido
    ? Math.min(100, Math.max(0, percentual))
    : 0;

  return (
    <section className="mt-card-ocupacao">
      <div className={`ocupacao-icone ${cor}`}>
        {icone}
      </div>

      <div className="ocupacao-conteudo">
        <span className="ocupacao-titulo">
          {titulo}
        </span>

        <div className="ocupacao-inferior">
          <div className="ocupacao-barra">
            <div
              className={`ocupacao-progresso ${cor}`}
              style={{ width: `${ocupacao}%` }}
            />
          </div>

          <strong>
            {valorValido ? `${ocupacao}%` : "—"}
          </strong>
        </div>
      </div>
    </section>
  );
}

export default CardOcupacao;
