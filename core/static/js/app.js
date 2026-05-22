const { useEffect } = React;

function Nav() {
  return (
    <nav className="nav">
      <span className="logo"><span className="dot" />Sanghelios</span>
      <div className="nav-links">
        <a href="#hero">Home</a>
        <a href="#upload">Upload</a>
      </div>
    </nav>
  );
}

function Hero() {
  return (
    <section className="section" id="hero">
      <div className="inner">
        <p className="eyebrow">Blood Donation Processing</p>
        <h1>Sanghelios</h1>
        <a href="#upload" className="btn">Get Started</a>
      </div>
    </section>
  );
}

function Upload() {
  return (
    <section className="section" id="upload">
      <div className="inner">
        <p className="eyebrow">Data Import</p>
        <h2>Upload Records</h2>
        <p className="body-text">Import donor CSV files to begin processing.</p>
        <a href="/processing" className="btn btn-outline">Go to Processing</a>
      </div>
    </section>
  );
}

function App() {
  useEffect(() => {
    const io = new IntersectionObserver(
      entries => entries.forEach(e => e.target.classList.toggle('visible', e.isIntersecting)),
      { threshold: 0.25 }
    );
    document.querySelectorAll('.section').forEach(s => io.observe(s));
    return () => io.disconnect();
  }, []);

  return (
    <>
      <Nav />
      <Hero />
      <Upload />
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);