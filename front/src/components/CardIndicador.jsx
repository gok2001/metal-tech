
import "../styles/CardIndicador.css";

function CardIndicador({ titulo, valor, icone, cor = "azul", legenda }) {
  const valorExibido =
    valor === null || valor === undefined
      ? "—"
      : typeof valor === "number"
        ? valor.toLocaleString("pt-BR")
        : valor;

  return (
    <section className="mt-card mt-indicador">
      <div className={`mt-indicador-icone ${cor}`}>
        {icone}
      </div>

      <div className="mt-indicador-texto">
        <span className="mt-indicador-titulo">{titulo}</span>

        <div className="mt-indicador-linha">
          <strong>{valorExibido}</strong>
        </div>

        {legenda && <small>{legenda}</small>}
      </div>
    </section>
  );
}

export default CardIndicador;
