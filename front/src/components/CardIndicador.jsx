import "../styles/CardIndicador.css";

function CardIndicador(props) {
  var cor = props.cor || "azul";
  var valor = props.valor;

  // sem dado ainda: mostra um traço, e não um zero inventado
  var valorExibido = "—";
  if (typeof valor === "number") {
    valorExibido = valor.toLocaleString("pt-BR");
  } else if (valor !== null && valor !== undefined) {
    valorExibido = valor;
  }

  return (
    <section className="mt-card mt-indicador">
      <div className={"mt-indicador-icone " + cor}>
        {props.icone}
      </div>

      <div className="mt-indicador-texto">
        <span className="mt-indicador-titulo">{props.titulo}</span>

        <div className="mt-indicador-linha">
          <strong>{valorExibido}</strong>
        </div>

        {props.legenda && <small>{props.legenda}</small>}
      </div>
    </section>
  );
}

export default CardIndicador;