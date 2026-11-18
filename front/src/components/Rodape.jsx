import { Clock } from "lucide-react";
import "../styles/Rodape.css";

// coloca um zero na frente quando o número tem só um dígito (5 vira "05")
function dois(numero) {
  if (numero < 10) {
    return "0" + numero;
  }
  return "" + numero;
}

// formata data e hora ex "16:30 - 11/11/2026"
function formatarDataHora(valor) {
  if (!valor) {
    return "—";
  }

  var data = new Date(valor);
  if (isNaN(data.getTime())) {
    return "—";
  }

  var hora = dois(data.getHours()) + ":" + dois(data.getMinutes());
  var dia = dois(data.getDate()) + "/" + dois(data.getMonth() + 1) + "/" + data.getFullYear();

  return hora + " - " + dia;
}


// amostra off ou on api 
function Rodape(props) {
  var classe = "mt-rodape-api";
  var texto = "API conectada";

  if (!props.online) {
    classe = "mt-rodape-api offline";
    texto = "API desconectada";
  }

  return (
    <footer className="mt-card mt-rodape">
      <span className="mt-rodape-hora">
        <Clock size={20} />
        Última atualização: {formatarDataHora(props.ultimaAtualizacao)}
      </span>

      <span className={classe}>
        <span className="mt-bolinha"></span> {texto}
      </span>
    </footer>
  );
}

export default Rodape;