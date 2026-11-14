import "../styles/CardOcupacao.css";

// confere se o valor é um número de verdade
function ehNumero(valor) {
  return typeof valor === "number" && isFinite(valor);
}

function formatar(valor) {
  return valor.toLocaleString("pt-BR");
}

function CardOcupacao(props) {
  var cor = props.cor || "azul";
  var quantidade = props.quantidade;
  var capacidade = props.capacidade;

  // só calcula se os dois valores forem válidos (evita dividir por zero)
  var dadosValidos = ehNumero(quantidade) && quantidade >= 0 && ehNumero(capacidade) && capacidade > 0;

  var percentual = null;
  var largura = 0;
  if (dadosValidos) {
    percentual = (quantidade / capacidade) * 100;
    largura = Math.min(100, Math.max(0, percentual));
  }

  var textoValores = "— / —";
  var textoPercentual = "—";
  if (dadosValidos) {
    textoValores = formatar(quantidade) + " / " + formatar(capacidade);
    textoPercentual = percentual.toFixed(0) + "%";
  }

  return (
    <section className={"mt-card-ocupacao " + cor}>
      <div className={"ocupacao-icone " + cor}>
        {props.icone}
      </div>

      <div className="ocupacao-conteudo">
        <span className="ocupacao-titulo">
          {props.titulo}
        </span>

        <div className="ocupacao-inferior">
          <div className="ocupacao-barra">
            <div
              className={"ocupacao-progresso " + cor}
              style={{ width: largura + "%" }}
            />

            <span className="ocupacao-valores">
              {textoValores}
            </span>
          </div>

          <strong className="ocupacao-percentual">
            {textoPercentual}
          </strong>
        </div>
      </div>
    </section>
  );
}

export default CardOcupacao;