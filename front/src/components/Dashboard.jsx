
import { useState, useEffect } from "react";

import Header from "./Header.jsx";
import CaixaTeste from "./CaixaTeste.jsx";
import CardIndicador from "./CardIndicador.jsx";
import CardOcupacao from "./CardOcupacao.jsx";

import GraficoDistribuicao from "./GraficoDistribuicao.jsx";
import GraficoProducao from "./GraficoProducao.jsx";
import GraficoReservatorio from "./GraficoReservatorio.jsx";

import { buscarDados } from "../services/api.js";

import {
  Box,
  Settings,
  Recycle
} from "lucide-react";

var CAMINHO_RA = "";

function Dashboard() {
  const [online, setOnline] = useState(false);

  const [dados, setDados] = useState({
    total_pecas: null,
    pecas_metalicas: null,
    pecas_nao_metalicas: null,

    historico_producao: [],

    ultima_atualizacao: null
  });

  useEffect(() => {
    function carregarDados() {
      buscarDados()
        .then((resposta) => {
          setOnline(true);

          if (resposta) {
            setDados((anterior) => ({
              ...anterior,
              ...resposta
            }));
          }
        })
        .catch(() => {
          setOnline(false);
        });
    }

    carregarDados();

    const intervalo = setInterval(carregarDados, 5000);

    return () => clearInterval(intervalo);
  }, []);

  return (
    <div className="mt-pagina container">

      {/* CABEÇALHO */}
      <Header
        online={online}
        caminhoRA={CAMINHO_RA}
      />

      {/* PRIMEIRA LINHA: CINCO CARDS */}
      <div className="row row-cols-2 row-cols-md-3 row-cols-xl-5 g-3 mb-3">

        {/* TOTAL DE PEÇAS */}
        <div className="col">
          <CardIndicador
            titulo="Total de Peças"
            valor={dados.total_pecas}
            icone={<Box size={32} color="#00BFFF" />}
            cor="azul"
          />
        </div>

        {/* PEÇAS METÁLICAS */}
        <div className="col">
          <CardIndicador
            titulo="Peças Metálicas"
            valor={dados.pecas_metalicas}
            icone={<Settings size={32} color="#00BFFF" />}
            cor="azul"
          />
        </div>

        {/* PEÇAS NÃO METÁLICAS */}
        <div className="col">
          <CardIndicador
            titulo="Peças Não Metálicas"
            valor={dados.pecas_nao_metalicas}
            icone={<Recycle size={32} color="#FFAE00" />}
            cor="laranja"
          />
        </div>

        {/* OCUPAÇÃO DO RESERVATÓRIO METÁLICO */}
        <div className="col">
          <CardOcupacao
            titulo="Reservatório Metálico"
            percentual={0}
            icone={<Settings size={32} />}
            cor="azul"
          />
        </div>

        {/* OCUPAÇÃO DO RESERVATÓRIO NÃO METÁLICO */}
        <div className="col">
          <CardOcupacao
            titulo="Reservatório Não Metálico"
            percentual={0}
            icone={<Recycle size={32} />}
            cor="laranja"
          />
        </div>

      </div>

      {/* SEGUNDA LINHA: GRÁFICOS */}
      <div className="row g-3 mb-3">

        <div className="col-12 col-lg-6 col-xl-4">
          <GraficoProducao
            dados={dados.historico_producao}
          />
        </div>

        <div className="col-12 col-lg-6 col-xl-4">
          <GraficoReservatorio />
        </div>

        <div className="col-12 col-xl-4">
          <GraficoDistribuicao
            metalicas={dados.pecas_metalicas}
            naoMetalicas={dados.pecas_nao_metalicas}
            total={dados.total_pecas}
          />
        </div>

      </div>

      {/* TERCEIRA LINHA: CIÊNCIA DE DADOS */}
      <div className="row g-3 mb-3">

        <div className="col-12 col-xl-4">
          <CaixaTeste
            titulo="Estatísticas Descritivas"
            altura={240}
          />
        </div>

        <div className="col-12 col-md-6 col-xl-4">
          <CaixaTeste
            titulo="Histograma do Estoque"
            altura={240}
          />
        </div>

        <div className="col-12 col-md-6 col-xl-4">
          <CaixaTeste
            titulo="Boxplot do Estoque"
            altura={240}
          />
        </div>

      </div>

      {/* RODAPÉ */}
      <CaixaTeste
        titulo="Rodapé"
        altura={50}
      />

    </div>
  );
}

export default Dashboard;
