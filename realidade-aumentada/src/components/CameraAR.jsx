
import { useEffect, useRef, useState } from "react";
import { MindARThree } from "mind-ar/dist/mindar-image-three.prod.js";

// Tempo de tolerância ao perder o reconhecimento
const TEMPO_TOLERANCIA = 1000;

// Endereço do Dashboard
const DASHBOARD_URL =
  import.meta.env.VITE_DASHBOARD_URL ||
  "http://localhost:5173/";

export default function CameraAR({ onDetected }) {
  const containerRef = useRef(null);
  const mindarRef = useRef(null);

  const iniciandoRef = useRef(false);
  const onDetectedRef = useRef(onDetected);

  const timeoutRef = useRef(null);
  const detectadaRef = useRef(false);

  const [status, setStatus] = useState("Aguardando câmera");
  const [iniciado, setIniciado] = useState(false);
  const [carregando, setCarregando] = useState(false);

  // Mantém a função de detecção atualizada
  useEffect(() => {
    onDetectedRef.current = onDetected;
  }, [onDetected]);

  // Cancela o temporizador de tolerância
  function cancelarTimeout() {
    if (timeoutRef.current !== null) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }

  // Libera recursos ao desmontar
  useEffect(() => {
    return () => {
      if (timeoutRef.current !== null) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      detectadaRef.current = false;

      if (mindarRef.current) {
        const mindar = mindarRef.current;

        mindarRef.current = null;
        mindar.renderer.setAnimationLoop(null);

        Promise.resolve(mindar.stop()).catch((erro) => {
          console.error("Erro ao liberar câmera:", erro);
        });
      }
    };
  }, []);

  // =====================================
  // INICIAR CÂMERA
  // =====================================

  async function iniciarCamera() {
    if (
      iniciandoRef.current ||
      iniciado ||
      mindarRef.current
    ) {
      return;
    }

    iniciandoRef.current = true;

    setCarregando(true);
    setStatus("Iniciando câmera...");

    cancelarTimeout();
    detectadaRef.current = false;

    let mindar = null;

    try {
      mindar = new MindARThree({
        container: containerRef.current,

        imageTargetSrc:
          `${import.meta.env.BASE_URL}target/esteira.mind`,

        maxTrack: 1,
        filterMinCF: 0.001,
        filterBeta: 1000,
      });

      mindarRef.current = mindar;

      const { renderer, scene, camera } = mindar;

      const anchor = mindar.addAnchor(0);

      // =====================================
      // ESTEIRA RECONHECIDA
      // =====================================

      anchor.onTargetFound = () => {
        if (mindarRef.current !== mindar) return;

        cancelarTimeout();

        detectadaRef.current = true;

        console.log("Esteira reconhecida!");

        setStatus("Esteira detectada");
        onDetectedRef.current?.(true);
      };

      // =====================================
      // RECONHECIMENTO PERDIDO
      // =====================================

      anchor.onTargetLost = () => {
        if (mindarRef.current !== mindar) return;

        detectadaRef.current = false;

        cancelarTimeout();

        setStatus("Verificando esteira...");

        timeoutRef.current = setTimeout(() => {
          timeoutRef.current = null;

          if (
            mindarRef.current !== mindar ||
            detectadaRef.current
          ) {
            return;
          }

          setStatus("Procurando esteira...");
          onDetectedRef.current?.(false);

        }, TEMPO_TOLERANCIA);
      };

      // =====================================
      // ATIVAR MINDAR
      // =====================================

      await mindar.start();

      if (mindarRef.current !== mindar) {
        await mindar.stop();
        return;
      }

      // Ajusta a câmera para o contêiner
      requestAnimationFrame(() => {
        if (mindarRef.current === mindar) {
          mindar.resize();
        }
      });

      // Renderização contínua
      renderer.setAnimationLoop(() => {
        renderer.render(scene, camera);
      });

      setIniciado(true);

      setStatus(
        detectadaRef.current
          ? "Esteira detectada"
          : "Procurando esteira..."
      );

      console.log("Câmera iniciada com sucesso!");

    } catch (erro) {
      console.error("Erro ao iniciar MindAR:", erro);

      cancelarTimeout();
      detectadaRef.current = false;

      setStatus("Erro ao iniciar câmera");
      setIniciado(false);

      onDetectedRef.current?.(false);

      if (mindar) {
        mindar.renderer.setAnimationLoop(null);

        try {
          await mindar.stop();
        } catch (erroParada) {
          console.error(
            "Erro ao liberar câmera:",
            erroParada
          );
        }
      }

      if (mindarRef.current === mindar) {
        mindarRef.current = null;
      }

    } finally {
      iniciandoRef.current = false;
      setCarregando(false);
    }
  }

  // =====================================
  // PARAR CÂMERA
  // =====================================

  async function pararCamera() {
    if (iniciandoRef.current) return;

    cancelarTimeout();
    detectadaRef.current = false;

    const mindar = mindarRef.current;

    if (mindar) {
      mindarRef.current = null;
      mindar.renderer.setAnimationLoop(null);

      try {
        await mindar.stop();
      } catch (erro) {
        console.error("Erro ao parar câmera:", erro);
      }
    }

    onDetectedRef.current?.(false);

    setIniciado(false);
    setStatus("Câmera desligada");
  }

  // =====================================
  // INTERFACE
  // =====================================

  return (
    <div className="camera-ar">

      {/* Área da câmera */}
      <div
        ref={containerRef}
        className="camera-container"
      />

      {/* Controles e navegação */}
      <div className="camera-controles">

        <p>{status}</p>

        {!iniciado ? (
          <button
            type="button"
            onClick={iniciarCamera}
            disabled={carregando}
          >
            {carregando
              ? "Iniciando..."
              : "Iniciar câmera"}
          </button>
        ) : (
          <button
            type="button"
            onClick={pararCamera}
          >
            Parar câmera
          </button>
        )}

        <a
          href={DASHBOARD_URL}
          className="voltar-dashboard"
          aria-label="Voltar ao Dashboard"
        >
          Voltar
        </a>

      </div>

    </div>
  );
}
