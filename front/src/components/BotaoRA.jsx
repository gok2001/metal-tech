import "../styles/BotaoRA.css";
import iconeCaixa from "../images/icon-caixa.png";
import iconeBranco from "../images/icon-branco.png";

function BotaoRA(props) {
  var classe = "mt-botao-ra";
  var destino = props.caminho;

  if (!props.caminho) {
    classe = "mt-botao-ra desativado";
    destino = undefined;
  }

  return (
    <div className="mt-ra">
      <img className="mt-ra-icone" src={iconeCaixa} alt="" />

      <div className="mt-ra-texto">
        <strong>Dados da produção agora em Realidade Aumentada</strong>
        <small>Acesse a câmera e visualize as informações em tempo real diretamente na esteira.</small>
      </div>

      <a href={destino} className={classe}>
        <span className="mt-botao-icone">
          <img src={iconeBranco} alt="" />
        </span>
        <span>Acessar Realidade Aumentada</span>
        <span>&gt;</span>
      </a>
    </div>
  );
}

export default BotaoRA;