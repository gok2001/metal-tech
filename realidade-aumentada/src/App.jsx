
import { useEffect, useState } from "react";

import CameraAR from "./components/CameraAR";
import CardsInformativos from "./components/CardsInformativos";
import ElementosFixos from "./components/ElementosFixos";
import "./styles/ElementosFixosHud.css";
import "./App.css";

import {
  buscarDados,
  apiConfigurada,
} from "./services/api";

import "./App.css";

const INTERVALO_ATUALIZACAO = 5000;

export default function App() {
  const [esteiraDetectada, setEsteiraDetectada] = useState(false);

  const [dados, setDados] = useState(null);
  const [conexao, setConexao] = useState("aguardando");

  useEffect(() => {
    // Não realiza requisições enquanto não houver API.
    if (!apiConfigurada()) return;

    let ativo = true;
    let consultando = false;
    let controller = null;

    async function atualizarDados() {
      if (consultando) return;

      consultando = true;
      controller = new AbortController();

      try {
        const resultado = await buscarDados(controller.signal);

        if (!ativo) return;

        setDados(resultado);
        setConexao("conectado");
      } catch (erro) {
        if (!ativo || erro.name === "AbortError") return;

        console.error("Erro ao buscar dados:", erro);

        setDados(null);
        setConexao("erro");
      } finally {
        consultando = false;
      }
    }

    atualizarDados();

    const intervalo = setInterval(
      atualizarDados,
      INTERVALO_ATUALIZACAO
    );

    return () => {
      ativo = false;
      clearInterval(intervalo);
      controller?.abort();
    };
  }, []);

  return (
    <main className="app">
      <CameraAR onDetected={setEsteiraDetectada} />

      <ElementosFixos conexao={conexao} />

      {esteiraDetectada && (
        <CardsInformativos dados={dados} />
      )}
    </main>
  );
}
