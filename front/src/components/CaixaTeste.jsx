function CaixaTeste(props) {
  return (
    <section className="mt-card mt-caixa" style={{ minHeight: props.altura }}>
      <h3>{props.titulo}</h3>
      <div className="mt-caixa-corpo">em construção</div>
    </section>
  );
}

export default CaixaTeste;