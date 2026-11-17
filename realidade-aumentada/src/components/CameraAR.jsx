
import { useEffect, useRef, useState } from "react";
import { MindARThree } from "mind-ar/dist/mindar-image-three.prod.js";

// Tempo de tolerância ao perder a imagem
const TEMPO_TOLERANCIA = 1000;

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

  useEffect(() => {
    onDetectedRef.current = onDetected;
  }, [onDetected]);

  function cancelarTimeout() {
    if (timeoutRef.current !== null) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }

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
        mindar.stop();
      }
    };
  }, []);

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
        imageTargetSrc: `${import.meta.env.BASE_URL}target/esteira.mind`,
        maxTrack: 1,
        filterMinCF: 0.001,
        filterBeta: 1000,
      });

      mindarRef.current = mindar;

      const { renderer, scene, camera } = mindar;
      const anchor = mindar.addAnchor(0);

      // ESTEIRA RECONHECIDA
      anchor.onTargetFound = () => {
        if (mindarRef.current !== mindar) return;

        cancelarTimeout();

        detectadaRef.current = true;

        console.log("Esteira reconhecida!");

        setStatus("Esteira detectada");
        onDetectedRef.current?.(true);
      };

      // RECONHECIMENTO PERDIDO
      anchor.onTargetLost = () => {
        if (mindarRef.current !== mindar) return;

        console.log("Reconhecimento temporariamente perdido");

        detectadaRef.current = false;

        cancelarTimeout();

        setStatus("Verificando esteira...");

        // Aguarda antes de esconder os cards
        timeoutRef.current = setTimeout(() => {
          timeoutRef.current = null;

          if (
            mindarRef.current !== mindar ||
            detectadaRef.current
          ) {
            return;
          }

          console.log("Esteira não detectada");

          setStatus("Procurando esteira...");
          onDetectedRef.current?.(false);
        }, TEMPO_TOLERANCIA);
      };

      // INICIA A CÂMERA
      await mindar.start();

      if (mindarRef.current !== mindar) {
        await mindar.stop();
        return;
      }

      // MANTÉM O AJUSTE FULLSCREEN
      requestAnimationFrame(() => {
        if (mindarRef.current === mindar) {
          mindar.resize();
        }
      });

      // RENDERIZAÇÃO
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

  async function pararCamera() {
    if (iniciandoRef.current) return;

    // Cancela qualquer espera pendente
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

    // Esconde imediatamente os cards ao parar
    onDetectedRef.current?.(false);

    setIniciado(false);
    setStatus("Câmera desligada");
  }

  return (
    <div className="camera-ar">
      <div
        ref={containerRef}
        className="camera-container"
      />

      <div className="camera-controles">
        <p>{status}</p>

        {!iniciado ? (
          <button
            onClick={iniciarCamera}
            disabled={carregando}
          >
            {carregando
              ? "Iniciando..."
              : "Iniciar câmera"}
          </button>
        ) : (
          <button onClick={pararCamera}>
            Parar câmera
          </button>
        )}
      </div>
    </div>
  );
}
