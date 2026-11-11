import logoImg from '../images/logo-icone.png'

function Header(props) {
  var classe = "mt-status-online";
  var texto = "Sistema Online";

  if (!props.online) {
    classe = "mt-status-online offline";
    texto = "Sistema Offline";
  }

  return (
    <header className="mt-card mt-header">
      <div className="mt-logo"><img src={logoImg} alt="Logo Metaltech" /></div>
      <div className="mt-divisor"></div>
      <div className="mt-header-texto">
        <h1>METALTECH</h1>
        <p>Monitoramento Industrial</p>
      </div>
      <span className={classe}>
        <span className="mt-bolinha"></span> {texto}
      </span>
    </header>
  );
}

export default Header;