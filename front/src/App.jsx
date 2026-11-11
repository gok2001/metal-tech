import { useState, useEffect } from "react";
import Header from "./components/Header.jsx";
import BotaoRA from "./components/BotaoRA.jsx";
import { buscarDados } from "./services/api.js";
import "./styles/Dashboard.css";
import "./styles/BotaoRA.css";

function App () {
  var [online, setOnline] = useState(true);

  useEffect(function () {
    buscarDados()
      .then(function (dados) {
        setOnline(true);
      })
      .catch(function () {
        setOnline(false);
      });
  }, []);

  return (
    <div className="mt-pagina container">
      <Header online={online} />
      <BotaoRA />
    </div>
  );
}
export default App;