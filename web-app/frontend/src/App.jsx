import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import ShiftReport from './pages/ShiftReport';
import SalaryReport from './pages/SalaryReport';
import TransactionReport from './pages/TransactionReport';
import Settings from './pages/Settings';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/shift-report" element={<ShiftReport />} />
            <Route path="/salary-report" element={<SalaryReport />} />
            <Route path="/transaction-report" element={<TransactionReport />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
