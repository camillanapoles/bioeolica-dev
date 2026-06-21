import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [simulations, setSimulations] = useState<Array<any>>([]);
  const [newSimName, setNewSimName] = useState('');
  const [newSimDesc, setNewSimDesc] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSimulations();
  }, []);

  const fetchSimulations = async () => {
    try {
      const resp = await axios.get(`${API_BASE}/simulations/`);
      setSimulations(resp.data);
    } catch (e) {
      console.error('Failed to fetch simulations', e);
    }
  };

  const createSimulation = async () => {
    if (!newSimName.trim()) return;
    setLoading(true);
    try {
      const resp = await axios.post(`${API_BASE}/simulations/`, {
        name: newSimName,
        description: newSimDesc,
        parameters: {
          solvers: ['openfoam'],
          openfoam_params: {
            velocity: 10,
            viscosity: 1.5e-5,
          },
        },
      });
      setSimulations([...simulations, resp.data]);
      setNewSimName('');
      setNewSimDesc('');
    } catch (e) {
      console.error('Failed to create simulation', e);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async (id: string) => {
    try {
      await axios.post(`${API_BASE}/simulations/${id}/run`);
      alert('Simulation started');
    } catch (e) {
      console.error('Failed to run simulation', e);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Virtual Lab Platform</h1>

      <div style={{ marginBottom: '20px' }}>
        <h2>Create New Simulation</h2>
        <input
          type="text"
          placeholder="Simulation name"
          value={newSimName}
          onChange={(e) => setNewSimName(e.target.value)}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <input
          type="text"
          placeholder="Description"
          value={newSimDesc}
          onChange={(e) => setNewSimDesc(e.target.value)}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <button onClick={createSimulation} disabled={loading}>
          {loading ? 'Creating...' : 'Create Simulation'}
        </button>
      </div>

      <div>
        <h2>Simulations</h2>
        {simulations.length === 0 ? (
          <p>No simulations yet.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {simulations.map((sim) => (
              <li
                key={sim.id}
                style={{
                  border: '1px solid #ddd',
                  margin: '10px 0',
                  padding: '15px',
                  borderRadius: '5px',
                }}
              >
                <div>
                  <strong>{sim.name}</strong> ({sim.status})
                </div>
                <div style={{ fontSize: '0.9em', color: '#666' }}>
                  {sim.description || '(no description)'}
                </div>
                <div style={{ marginTop: '10px' }}>
                  <button
                    onClick={() => runSimulation(sim.id)}
                    disabled={sim.status === 'running'}
                  >
                    {sim.status === 'running' ? 'Running...' : 'Run Simulation'}
                  </button>
                  <button
                    onClick={() => {
                      // In a real app, navigate to detail view
                      alert('View results not implemented yet');
                    }}
                    style={{ marginLeft: '10px' }}
                  >
                    View Results
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App;
