    import "../styles/BotaoRA.css";
    import iconeCaixa from '../images/icon-caixa.png';
    import iconeBranco from '../images/icon-branco.png';

    function BotaoRA() {
    return (
        <section className="mt-card mt-ar">
        <div className="mt-ar-icone">
            <img src={iconeCaixa} alt="icon-caixa" />
        </div>
        <h2>Dados da produção agora em Realidade Aumentada</h2>
        <p>Acesse a câmera e visualize as informações em tempo real diretamente na esteira.</p>

        <a href="/ra" className="mt-botao-ra">
            <span className="mt-botao-icone">
            <img src={iconeBranco} alt="icon-branco" />
            </span>
            <span className="mt-botao-texto">Acessar Realidade Aumentada</span>
            <span className="mt-botao-seta">&gt;</span>
        </a>
        </section>
    );
    }

    export default BotaoRA;