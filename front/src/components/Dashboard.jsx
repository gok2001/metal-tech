
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

// Conexão APIs
import { buscarDados } from "../services/api.js";
import { buscarEstatisticasReservatorios } from "../services/estatisticas.js";


import { Box, Settings, Recycle } from "lucide-react";

// Endereço da Realidade Aumentada
var CAMINHO_RA = "https://localhost:5174";

function Dashboard() {
  
  // estado se esta on ou off
  var [online, setOnline] = useState(false);

  var [ultimaAtualizacao, setUltimaAtualizacao] =
    useState(null);

  // Dados dos utilizado nos graficos e reservatorio
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

    // Estatísticas calculadas pela Ciência de Dados
    estatisticas_producao: null,
    estatisticas_reservatorio_metalico: null,
    estatisticas_reservatorio_nao_metalico: null,
  });

  // Consultar back

  useEffect(function () {
    var ativo = true;
    var consultando = false;

    async function carregarDados() {
      // Evita requisições sobrepostas
      if (consultando) return;

      consultando = true;

      try {
        const resposta = await buscarDados();

        if (!ativo) return;

        if (resposta) {
          setOnline(true);

          // Atualiza somente os campos recebidos
          setDados(function (anterior) {
            return {
              ...anterior,
              ...resposta,
            };
          });

          setUltimaAtualizacao(
            resposta.ultima_atualizacao || new Date()
          );
        } else {
          setOnline(false);
        }
      } catch (erro) {
        if (ativo) {
          console.error(
            "Erro ao consultar o backend Java:",
            erro
          );

          setOnline(false);
        }
      } finally {
        consultando = false;
      }
    }

    // Primeira consulta ao abrir o dashboard
    carregarDados();

    // Atualiza a cada 30 segundos
    var intervalo = setInterval(
      carregarDados,
      30000
    );

    // Encerra consultas periódicas ao desmontar
    return function () {
      ativo = false;
      clearInterval(intervalo);
    };
  }, []);

  // consulta CIDA

  useEffect(function () {
    var ativo = true;
    var consultando = false;

    async function atualizarEstatisticas() {
      // Evita consultas simultâneas
      if (consultando) return;

      consultando = true;

      try {
        const resultado =
          await buscarEstatisticasReservatorios();

        if (!ativo) return;

        // Adiciona as estatísticas ao estado
        // sem apagar os dados da produção
        setDados(function (anterior) {
          return {
            ...anterior,
            ...resultado,
          };
        });
      } catch (erro) {
        console.error(
          "Erro ao consultar estatísticas Python:",
          erro
        );

        if (ativo) {
          // Não apresenta estatísticas antigas
          // como se fossem dados atualizados
          setDados(function (anterior) {
            return {
              ...anterior,
              estatisticas_reservatorio_metalico: null,
    estatisticas_reservatorio_nao_metalico: null,
              boxplot_reservatorio: null,
              historico_reservatorio: [],
              histograma_reservatorio: [],
            };
          });
        }
      } finally {
        consultando = false;
      }
    }

    // Primeira consulta ao abrir o dashboard
    atualizarEstatisticas();

    // Atualiza dados
    var intervalo = setInterval(
      atualizarEstatisticas,
      30000
    );

    return function () {
      ativo = false;
      clearInterval(intervalo);
    };
  }, []);

  var estatisticasProducao =
    dados.estatisticas_producao || {};

  return (
    <div className="mt-pagina container">

      {/* CABEÇALHO */}
      <Header
        online={online}
        caminhoRA={CAMINHO_RA}
      />

      {/* Linha dos cards */}

      <div className="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-xxl-5 g-3 mb-3">

        {/* TOTAL DE PEÇAS */}
        <div className="col">
          <CardIndicador
            titulo="Total de Peças"
            valor={dados.total_pecas}
            icone={
              <Box size={32} color="#00BFFF" />
            }
            cor="azul"
          />
        </div>

        {/* PEÇAS METÁLICAS */}
        <div className="col">
          <CardIndicador
            titulo="Peças Metálicas"
            valor={dados.pecas_metalicas}
            icone={
              <Settings size={32} color="#00BFFF" />
            }
            cor="azul"
          />
        </div>

        {/* PEÇAS NÃO METÁLICAS */}
        <div className="col">
          <CardIndicador
            titulo="Peças Não Metálicas"
            valor={dados.pecas_nao_metalicas}
            icone={
              <Recycle size={32} color="#FFAE00" />
            }
            cor="laranja"
          />
        </div>

        {/* RESERVATÓRIO METÁLICO */}
        <div className="col">
          <CardOcupacao
            titulo="Reservatório Metálico"
            quantidade={
              dados.quantidade_reservatorio_metalico
            }
            capacidade={
              dados.capacidade_reservatorio_metalico
            }
            icone={<Box size={32} />}
            cor="azul"
          />
        </div>

        {/* RESERVATÓRIO NÃO METÁLICO */}
        <div className="col">
          <CardOcupacao
            titulo="Reservatório Não Metálico"
            quantidade={
              dados.quantidade_reservatorio_nao_metalico
            }
            capacidade={
              dados.capacidade_reservatorio_nao_metalico
            }
            icone={<Recycle size={32} />}
            cor="laranja"
          />
        </div>

      </div>

      {/* graficos abaixo feito com auxilio i.a */}

      <div className="row g-3 mb-3">

        {/* grafoco produção */}
        <div className="col-12 col-lg-6 col-xl-4">
          <GraficoProducao
            dados={dados.historico_producao}
          />
        </div>

        {/* grafico reservatorio */}
        <div className="col-12 col-lg-6 col-xl-4">
          <GraficoReservatorio
            dados={dados.historico_reservatorio}
          />
        </div>

        {/* grafico pizza */}
        <div className="col-12 col-xl-4">
          <GraficoDistribuicao
            metalicas={dados.pecas_metalicas}
            naoMetalicas={dados.pecas_nao_metalicas}
            total={dados.total_pecas}
          />
        </div>

      </div>

      {/* Parte da CIDa*/}

      <div className="row g-3 mb-3">

        {/* estatistica */}
        <div className="col-12 col-xl-4">
          <EstatisticasDescritivas
            metalicas={
              estatisticasProducao.metalicas
            }
            naoMetalicas={
              estatisticasProducao.naoMetalicas
            }
            estoqueMetalico={
              dados.estatisticas_reservatorio_metalico
            }
            estoqueNaoMetalico={
              dados.estatisticas_reservatorio_nao_metalico
            }
          />
        </div>

        {/* histograma */}
        <div className="col-12 col-md-6 col-xl-4">
          <HistogramaReservatorio
            dados={dados.histograma_reservatorio}
          />
        </div>

        {/* boxplot */}
        <div className="col-12 col-md-6 col-xl-4">
          <BoxplotReservatorio
            dados={dados.boxplot_reservatorio}
          />
        </div>

      </div>

      {/*rodape*/}

      <Rodape
        online={online}
        ultimaAtualizacao={ultimaAtualizacao}
      />

    </div>
  );
}

export default Dashboard;
