
import {
  Factory,
  Activity,
  ScanLine,
} from "lucide-react";

export default function ElementosFixos({ conexao = "aguardando" }) {
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

  return (
    <div className="elementos-fixos">
      <header className="ar-logo hud-card">
        <Factory className="logo-icone" size="1em" />

        <div>
          <h1>METALTECH</h1>
          <p>Realidade Aumentada</p>
        </div>
      </header>

      <div className="ar-conexao hud-card">
        <span
          className="indicador-conexao"
          style={{ backgroundColor: corConexao }}
        />
        <span>{textoConexao}</span>
      </div>

      <div className="ar-sistema hud-card">
        <Activity className="sistema-icone" size="1em" />

        <div>
          <strong>Status do sistema</strong>
          <p>
            {conectado
              ? "Dados recebidos"
              : erro
                ? "Falha na comunicação"
                : "Aguardando dados"}
          </p>
        </div>
      </div>

      <div className="ar-identificacao hud-card">
        <ScanLine className="ar-icone" size="1em" />

        <div>
          <strong>MetalTech AR</strong>
          <p>
            Visualização em tempo real da esteira de triagem
          </p>
        </div>
      </div>
    </div>
  );
}
