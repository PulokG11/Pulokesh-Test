import { NavLink, Route, Routes } from 'react-router-dom';
import { ChampionshipPage } from './pages/ChampionshipPage';
import { HomePage } from './pages/HomePage';
import { PlayPage } from './pages/PlayPage';
import './App.css';

function App() {
  return (
    <div className="app-shell">
      <nav className="topnav">
        <NavLink to="/" className="brand">
          Coffee Bean Optimization
        </NavLink>
        <div className="nav-links">
          <NavLink to="/play">Play</NavLink>
          <NavLink to="/championship">Championship</NavLink>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/play" element={<PlayPage />} />
        <Route path="/championship" element={<ChampionshipPage />} />
      </Routes>
    </div>
  );
}

export default App;
