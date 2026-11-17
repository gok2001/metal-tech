import { useState, useEffect } from "react";

import Header from "./Header.jsx";
import CardIndicador from "./CardIndicador.jsx";
import CardOcupacao from "./CardOcupacao.jsx";

import GraficoDistribuicao from "./GraficoDistribuicao.jsx";
import GraficoProducao from "./GraficoProducao.jsx";
import GraficoReservatorio from "./GraficoReservatorio.jsx";
import Rodape from "./Rodape.jsx";
import EstatisticasDescritivas from "./EstatisticasDescritivas.jsx";
import HistogramaReservatorio from "./HistogramaReservatorio.jsx";
import BoxplotReservatorio from "./BoxplotReservatorio.jsx";

import { buscarDados } from "../services/api.js";

import { Box, Settings, Recycle } from "lucide-react";

var CAMINHO_RA = "";

function Dashboard() {
  var [online, setOnline] = useState(false);
  var [ultimaAtualizacao, setUltimaAtualizacao] = useState(null);

  // Todos os dados começam vazios.
  // Nenhum valor é simulado.
  var [dados, setDados] = useState({
    // Contadores gerais
    total_pecas: null,
    pecas_metalicas: null,
    pecas_nao_metalicas: null,

    // Reservatório metálico
    quantidade_reservatorio_metalico: null,
    capacidade_reservatorio_metalico: null,

    // Reservatório não metálico
    quantidade_reservatorio_nao_metalico: null,
    capacidade_reservatorio_nao_metalico: null,

    // Históricos dos gráficos
    boxplot_reservatorio: null,
    histograma_reservatorio: [],
    historico_producao: [],
    historico_reservatorio: [],

    // Estatísticas calculadas pelo back-end
    estatisticas_producao: null,
    estatisticas_reservatorio: null,
  });

  useEffect(function () {
    var ativo = true;

    function carregarDados() {
      buscarDados()
        .then(function (resposta) {
          if (!ativo) return;

          if (resposta) {
            setOnline(true);

            // Atualiza os dados recebidos da API
            setDados(function (anterior) {
              return Object.assign({}, anterior, resposta);
            });

            // Última atualização bem-sucedida
            setUltimaAtualizacao(resposta.ultima_atualizacao || new Date());
          } else {
            setOnline(false);
          }
        })
        .catch(function () {
          if (ativo) {
            setOnline(false);
          }
        });
    }

    carregarDados();

    // Consulta a API a cada 5 segundos
    var intervalo = setInterval(carregarDados, 5000);

    return function () {
      ativo = false;
      clearInterval(intervalo);
    };
  }, []);

  var estatisticasProducao = dados.estatisticas_producao || {};

  return (
    <div className="mt-pagina container">
      {/* CABEÇALHO */}
      <Header online={online} caminhoRA={CAMINHO_RA} />

      {/* PRIMEIRA LINHA: CINCO CARDS */}
      <div className="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-xxl-5 g-3 mb-3">
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

        {/* RESERVATÓRIO METÁLICO */}
        <div className="col">
          <CardOcupacao
            titulo="Reservatório Metálico"
            quantidade={dados.quantidade_reservatorio_metalico}
            capacidade={dados.capacidade_reservatorio_metalico}
            icone={<Box size={32} />}
            cor="azul"
          />
        </div>

        {/* RESERVATÓRIO NÃO METÁLICO */}
        <div className="col">
          <CardOcupacao
            titulo="Reservatório Não Metálico"
            quantidade={dados.quantidade_reservatorio_nao_metalico}
            capacidade={dados.capacidade_reservatorio_nao_metalico}
            icone={<Recycle size={32} />}
            cor="laranja"
          />
        </div>
      </div>

      {/* SEGUNDA LINHA: GRÁFICOS */}
      <div className="row g-3 mb-3">
        {/* GRÁFICO DE PRODUÇÃO */}
        <div className="col-12 col-lg-6 col-xl-4">
          <GraficoProducao dados={dados.historico_producao} />
        </div>

        {/* GRÁFICO DO RESERVATÓRIO */}
        <div className="col-12 col-lg-6 col-xl-4">
          <GraficoReservatorio dados={dados.historico_reservatorio} />
        </div>

        {/* GRÁFICO DE DISTRIBUIÇÃO */}
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
        {/* ESTATÍSTICAS DESCRITIVAS */}
        <div className="col-12 col-xl-4">
          <EstatisticasDescritivas
            metalicas={estatisticasProducao.metalicas}
            naoMetalicas={estatisticasProducao.naoMetalicas}
            estoque={dados.estatisticas_reservatorio}
          />
        </div>

        {/* HISTOGRAMA RESERVATÓRIO */}
        <div className="col-12 col-md-6 col-xl-4">
          <HistogramaReservatorio dados={dados.histograma_reservatorio} />
        </div>

        {/* BOXPLOT DO ESTOQUE */}
        <div className="col-12 col-md-6 col-xl-4">
          <BoxplotReservatorio dados={dados.boxplot_reservatorio} />
        </div>
      </div>

      {/* RODAPÉ */}
      <Rodape online={online} ultimaAtualizacao={ultimaAtualizacao} />
    </div>
  );
}

export default Dashboard;
