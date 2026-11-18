
import "../styles/CardOcupacao.css";
import { AlertTriangle } from "lucide-react";

// Confere se o valor recebido é um número válido
function ehNumero(valor) {
  return typeof valor === "number" && Number.isFinite(valor);
}

function formatar(valor) {
  return valor.toLocaleString("pt-BR");
}

function CardOcupacao(props) {
  var cor = props.cor || "azul";
  var quantidade = props.quantidade;
  var capacidade = props.capacidade;

  // Só calcula quando os dados da API são válidos
  var dadosValidos =
    ehNumero(quantidade) &&
    quantidade >= 0 &&
    ehNumero(capacidade) &&
    capacidade > 0;

  var percentual = null;
  var largura = 0;

  if (dadosValidos) {
    percentual = (quantidade / capacidade) * 100;

    // Limita apenas a largura visual da barra
    largura = Math.min(100, Math.max(0, percentual));
  }

  // Define a cor conforme a ocupação real
  var nivelOcupacao = "";

  if (dadosValidos) {
    if (percentual >= 80) {
      nivelOcupacao = "critico";
    } else if (percentual >= 60) {
      nivelOcupacao = "alerta";
    }
  }

  // Exibe o ícone somente quando a barra estiver vermelha
  var alertaCritico = nivelOcupacao === "critico";

  // Mantém os indicadores vazios quando não há dados
  var textoValores = "— / —";
  var textoPercentual = "—";

  if (dadosValidos) {
    textoValores =
      formatar(quantidade) + " / " + formatar(capacidade);

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
              className={
                "ocupacao-progresso " +
                cor +
                " " +
                nivelOcupacao
              }
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

      {/* Ícone de alerta no canto inferior esquerdo */}
      {alertaCritico && (
        <span
          className="ocupacao-alerta-icone"
          role="img"
          aria-label="Reservatório em nível crítico"
          title="Atenção: reservatório com 90% ou mais de ocupação"
        >
          <AlertTriangle
            size={23}
            fill="#facc15"
            color="#101820"
            strokeWidth={2.5}
            aria-hidden="true"
          />
        </span>
      )}
    </section>
  );
}

export default CardOcupacao;
