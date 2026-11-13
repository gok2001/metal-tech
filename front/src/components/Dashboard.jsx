import { useState, useEffect } from "react";
import Header from "./Header.jsx";
import CaixaTeste from "./CaixaTeste.jsx";
import CardIndicador from "./CardIndicador.jsx";
import GraficoDistribuicao from "./GraficoDistribuicao.jsx";
import GraficoProducao from "./GraficoProducao.jsx";
import GraficoReservatorio from "./GraficoReservatorio.jsx";
import { buscarDados } from "../services/api.js";


import { Box, Settings, Recycle, AlertTriangle } from "lucide-react";

var CAMINHO_RA = "";

// DADOS DE TESTE: só pra ver o visual. APAGAR quando a API mandar o histórico real.
var DADOS_TESTE_PRODUCAO = [
  { hora: "22:20", pecasMetalicas: 0, nao_metalicas: 0 },
  { hora: "22:30", pecasMetalicass: 0, nao_metalicas: 0 },
  { hora: "22:40", pecasMetalicas: 0, nao_metalicas: 0 },
  { hora: "22:50", pecasMetalicas: 0, nao_metalicas: 0 },
  { hora: "23:00", pecasMetalicas: 0, nao_metalicas: 0 }
];

function Dashboard() {
  var [online, setOnline] = useState(false);

  var [dados, setDados] = useState({
    total_pecas: 0,
    pecasMetalicas: 0,
    nao_metalicas: 0,
    quantidade_atual: 0,
    percentual_ocupacao: 0,
    vagas_disponiveis: 0,
    ultima_atualizacao: null,

    // para o grafico estatistico
    estatisticas_producao: null,
    estatisticas_reservatorio: null,
    histograma_reservatorio: [],
    boxplot_reservatorio: null,
    alertas: [],
    historico_producao: [],
    historico_: []
  });

  useEffect(function () {
    function carregarDados() {
      buscarDados()
        .then(function (resposta) {
          setOnline(true);
          if (resposta) {
            // junta o que veio da API com o que já tinha
            setDados(function (anterior) {
              return Object.assign({}, anterior, resposta);
            });
          }
        })
        .catch(function () {
          // Mantem os dados caso caia a conexão com a api
          setOnline(false);
        });
    }

    carregarDados();

    var intervalo = setInterval(carregarDados, 5000);

    return function () {
      clearInterval(intervalo);
    };
  }, []);

  // Usa o percentual vindo do back ou calcula caso venha nulo/zerado
  var porcentagemReservatorio = 0;
  if (dados.percentual_ocupacao > 0) {
    porcentagemReservatorio = Math.min(Math.round(dados.percentual_ocupacao), 100);
  } else if (dados.capacidade_maxima > 0) {
    porcentagemReservatorio = Math.min(
      Math.round((dados.quantidade_atual / dados.capacidade_maxima) * 100),
      100
    );
  }

  return (
    <div className="mt-pagina container">
      <Header online={online} caminhoRA={CAMINHO_RA} />

      {/* linha 1: cards de indicadores */}
      <div className="row g-3 mb-3">
        <div className="col-6 col-xl-2">
          <CardIndicador
            titulo="Total de Peças"
            valor={dados.total_pecas}
            icone={<Box size={28} color="#00BFFF" />}
            cor="azul"
          />
        </div>
        <div className="col-6 col-xl-2">
          <CardIndicador
            titulo="Peças Metálicas"
            valor={dados.pecas_metalicas}
            icone={<Settings size={28} color="#00BFFF" />}
            cor="azul"
          />
        </div>
        <div className="col-6 col-xl-2">
          <CardIndicador
            titulo="Peças Não Metálicas"
            valor={dados.pecas_nao_metalicas}
            icone={<Recycle size={28} color="#00DCA0" />}
            cor="verde"
          />
        </div>

        {/* Card de Peças em Reservatorio */}
        <div className="col-12 col-xl-4 order-last order-xl-0">
          <CardIndicador
            titulo="Peças no Reservatório"
            valor={dados.quantidade_atual + " / " + dados.capacidade_maxima}
            icone={<Box size={28} color="#00DCA0" />}
            cor="verde"
            legenda={
              <div className="mt-progresso-container">
                <div className="mt-barra-fundo">
                  <div
                    className="mt-barra-preenchida"
                    style={{ width: porcentagemReservatorio + "%" }}
                  ></div>
                </div>
                <span className="mt-porcentagem-texto">{porcentagemReservatorio}%</span>
              </div>
            }
          />
        </div>

        <div className="col-6 col-xl-2">
          <CardIndicador
            titulo="Vagas Disponíveis"
            valor={dados.vagas_disponiveis}
            icone={<AlertTriangle size={28} color="#FFB800" />}
            cor="amarelo"
          />
        </div>
      </div>

      {/* linha 2: gráficos */}
      <div className="row g-3 mb-3">
        <div className="col-12 col-lg-6 col-xl-4">
          {/* Quando a API estiver feita trocar DADOS_TESTE_PRODUCAO */}
          <GraficoProducao dados={DADOS_TESTE_PRODUCAO} />
        </div>

        <div className="col-12 col-lg-6 col-xl-4">
          <CaixaTeste titulo="Evolução do Reservatório" altura={260} />
        </div>

        <div className="col-12 col-xl-4">
          <GraficoDistribuicao
            metalicas={dados.pecas_metalicas}
            naoMetalicas={dados.pecas_nao_metalicas}
            total={dados.total_pecas}
          />
        </div>
      </div>

      {/* linha 3: estatísticas (vão consumir estatisticas_producao, estatisticas_Reservatorio, histograma, boxplot e alertas) */}
      <div className="row g-3 mb-3">
        <div className="col-12 col-xl-4"><CaixaTeste titulo="Estatísticas Descritivas" altura={240} /></div>
        <div className="col-12 col-md-6 col-xl-3"><CaixaTeste titulo="Histograma do Reservatorio" altura={240} /></div>
        <div className="col-12 col-md-6 col-xl-2"><CaixaTeste titulo="Boxplot do Reservatorio" altura={240} /></div>
        <div className="col-12 col-xl-3"><CaixaTeste titulo="Alertas e Insights" altura={240} /></div>
      </div>

      <CaixaTeste titulo="Rodapé" altura={50} />
    </div>
  );
}

export default Dashboard;