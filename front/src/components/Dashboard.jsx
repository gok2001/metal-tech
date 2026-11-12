import { useState, useEffect } from "react";
import Header from "./Header.jsx";
import CaixaTeste from "./CaixaTeste.jsx";
import CardIndicador from "./CardIndicador.jsx";
import { buscarDados } from "../services/api.js";

import { Box, Settings, Recycle, AlertTriangle } from "lucide-react";

var CAMINHO_RA = "";   

function Dashboard() {
  var [online, setOnline] = useState(false);
  
  // Estado alinhado exatamente com o contrato definido para o Python
  var [dados, setDados] = useState({
    total_pecas: 0,
    pecas_metalicas: 0,
    pecas_nao_metalicas: 0,
    quantidade_atual: 0,
    capacidade_maxima: 100,
    percentual_ocupacao: 0,
    vagas_disponiveis: 0,
    ultima_atualizacao: null,
    // Estruturas prontas para as linhas de gráficos e estatísticas
    estatisticas_producao: null,
    estatisticas_estoque: null,
    histograma_estoque: [],
    boxplot_estoque: null,
    alertas: [],
    historico_producao: []
  });

  useEffect(function () {
    function carregarDados() {
      buscarDados()
        .then(function (resposta) {
          setOnline(true);
          if (resposta) {
            setDados((prev) => ({
              ...prev,
              ...resposta
            }));
          }
        })
        .catch(function () {
          // Mantém os últimos dados válidos na tela se a conexão cair
          setOnline(false);
        });
    }

    carregarDados();

    var intervalo = setInterval(carregarDados, 3000);
    return () => clearInterval(intervalo);
  }, []);

  // Garante o percentual vindo do back ou calcula caso venha nulo/zerado
  var porcentagemEstoque = dados.percentual_ocupacao > 0 
    ? Math.min(Math.round(dados.percentual_ocupacao), 100)
    : (dados.capacidade_maxima > 0 
        ? Math.min(Math.round((dados.quantidade_atual / dados.capacidade_maxima) * 100), 100) 
        : 0);

  return (
    <div className="mt-pagina container">
      {/* Você também pode passar ultimaAtualizacao={dados.ultima_atualizacao} para o Header se quiser exibir lá */}
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
        
        {/* Card de Peças em Estoque */}
        <div className="col-12 col-xl-4 order-last order-xl-0">
          <CardIndicador 
            titulo="Peças em Estoque" 
            valor={`${dados.quantidade_atual} / ${dados.capacidade_maxima}`} 
            icone={<Box size={28} color="#00DCA0" />} 
            cor="verde"
            legenda={
              <div className="mt-progresso-container">
                <div className="mt-barra-fundo">
                  <div 
                    className="mt-barra-preenchida" 
                    style={{ width: `${porcentagemEstoque}%` }}
                  ></div>
                </div>
                <span className="mt-porcentagem-texto">{porcentagemEstoque}%</span>
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

      {/* linha 2: gráficos (vão consumir dados.historico_producao, pecas_metalicas e pecas_nao_metalicas) */}
      <div className="row g-3 mb-3">
        <div className="col-12 col-lg-6 col-xl-4"><CaixaTeste titulo="Evolução da Produção" altura={260} /></div>
        <div className="col-12 col-lg-6 col-xl-4"><CaixaTeste titulo="Evolução do Estoque" altura={260} /></div>
        <div className="col-12 col-xl-4"><CaixaTeste titulo="Distribuição de Peças" altura={260} /></div>
      </div>

      {/* linha 3: estatísticas (vão consumir estatisticas_producao, estatisticas_estoque, histograma, boxplot e alertas) */}
      <div className="row g-3 mb-3">
        <div className="col-12 col-xl-4"><CaixaTeste titulo="Estatísticas Descritivas" altura={240} /></div>
        <div className="col-12 col-md-6 col-xl-3"><CaixaTeste titulo="Histograma do Estoque" altura={240} /></div>
        <div className="col-12 col-md-6 col-xl-2"><CaixaTeste titulo="Boxplot do Estoque" altura={240} /></div>
        <div className="col-12 col-xl-3"><CaixaTeste titulo="Alertas e Insights" altura={240} /></div>
      </div>

      <CaixaTeste titulo="Rodapé" altura={50} />
    </div>
  );
}

export default Dashboard;