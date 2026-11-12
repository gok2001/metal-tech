import "../styles/CardIndicador.css";

function CardIndicador(props) {
  var valor = props.valor;
  if (typeof valor === "number") {
    valor = valor.toLocaleString("pt-BR");
  }

  // a variação só aparece se vier um valor (a API ainda não manda isso)
  var variacao = null;
  if (props.variacao !== undefined && props.variacao !== null) {
    var sinal = props.variacao >= 0 ? "+" : "";
    var seta = props.variacao >= 0 ? "↑" : "↓";
    var classe = props.variacao >= 0 ? "mt-variacao sobe" : "mt-variacao desce";
    variacao = <span className={classe}>{seta} {sinal}{props.variacao}%</span>;
  }

  return (
    <section className="mt-card mt-indicador">
      <div className={"mt-indicador-icone " + (props.cor || "verde")}>{props.icone}</div>

      <div className="mt-indicador-texto">
        <span className="mt-indicador-titulo">{props.titulo}</span>
        <div className="mt-indicador-linha">
          <strong>{valor}</strong>
          {variacao}
        </div>
        {props.legenda && <small>{props.legenda}</small>}
      </div>
    </section>
  );
}

export default CardIndicador;