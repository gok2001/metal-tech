import logoIcone from "../images/logo-icone.png";


import {
  Factory,
  Wifi,
  Activity,
  ScanLine,
} from "lucide-react";

export default function ElementosFixos({
  conexao = "aguardando",
}) {
  const conectado = conexao === "conectado";
  const erro = conexao === "erro";

  const textoConexao = conectado
    ? "Conectado"
    : erro
      ? "Sem conexão"
      : "Aguardando conexão";

  const corConexao = conectado
    ? "#00ff99"
    : erro
      ? "#ff5b5b"
      : "#89979b";

  const statusSistema = conectado
    ? "Dados recebidos"
    : erro
      ? "Falha na comunicação"
      : "Aguardando dados";

  return (
    <div className="elementos-fixos">


      {/* SUPERIOR ESQUERDO */}
      <header className="ar-logo hud-card">
        <img
          src={logoIcone}
          alt="Logo METALTECH"
          className="logo-icone"
        />

        <span className="hud-divisor" />

        <div className="hud-logo-texto">
          <h1>METALTECH</h1>
          <p>Realidade Aumentada</p>
        </div>
      </header>


      {/* SUPERIOR DIREITO */}
      <div className="ar-conexao hud-card">
        <span
          className="indicador-conexao"
          style={{ backgroundColor: corConexao }}
        />

        <span
          className="hud-texto-conexao"
          style={{ color: corConexao }}
        >
          {textoConexao}
        </span>

        <Wifi
          className="hud-wifi"
          style={{ color: corConexao }}
        />
      </div>

      {/* INFERIOR ESQUERDO */}
      <div className="ar-sistema hud-card">
        <div className="hud-status-icone">
          <Activity className="sistema-icone" />
        </div>

        <div className="hud-status-texto">
          <strong>Status do sistema</strong>
          <p>{statusSistema}</p>
        </div>
      </div>

      {/* INFERIOR DIREITO */}
      <div className="ar-identificacao hud-card">
        <div className="hud-ar-icone">
          <ScanLine className="ar-icone" />
        </div>

        <div className="hud-ar-texto">
          <strong>MetalTech AR</strong>
          <p>
            Visualização em tempo real da esteira de triagem
          </p>
        </div>
      </div>

    </div>
  );
}
