import BotaoRA from "./BotaoRA.jsx";
import logoImg from "../images/logo-icone.png";

function Header(props) {
  var classeStatus = "mt-status-online";
  var textoStatus = "Sistema Online";

  if (!props.online) {
    classeStatus = "mt-status-online offline";
    textoStatus = "Sistema Offline";
  }

  return (
    <header className="mt-card mt-header">
      <div className="mt-logo">
        <img src={logoImg} alt="Logo MetalTech" />
      </div>

      <div className="mt-divisor"></div>

      <div className="mt-header-texto">
        <h1>METALTECH</h1>
        <p>Monitoramento Industrial</p>
      </div>

      <BotaoRA caminho={props.caminhoRA} />

      <div className={classeStatus}>
        <span className="mt-bolinha"></span> {textoStatus}
      </div>
    </header>
  );
}

export default Header;