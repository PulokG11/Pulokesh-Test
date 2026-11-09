import { Link } from 'react-router-dom';

export function HomePage() {
  return (
    <main className="home">
      <section className="hero">
        <p className="eyebrow">Classroom optimization lab</p>
        <h1>Coffee Bean Optimization</h1>
        <p className="lede">
          Run a coffee shop under uncertainty. Brew, price, and staff across eight rounds—then
          compare your plan to an expected-profit optimum.
        </p>
        <div className="actions">
          <Link className="button" to="/play">
            Play the Game
          </Link>
          <Link className="button secondary" to="/championship">
            Championship Mode
          </Link>
        </div>
      </section>
      <section className="home-points">
        <article>
          <h2>Nonlinear trade-offs</h2>
          <p>Pricing, congestion, and waste bend the profit surface.</p>
        </article>
        <article>
          <h2>Simulation under risk</h2>
          <p>Poisson arrivals make every day different—judge decisions in expectation.</p>
        </article>
        <article>
          <h2>Class championships</h2>
          <p>Share a match code, collect scores, and export a leaderboard.</p>
        </article>
      </section>
    </main>
  );
}
