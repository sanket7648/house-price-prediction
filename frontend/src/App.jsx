import { useState } from 'react';
import { Home, MapPin, Users, DoorOpen, BedDouble, Calendar, Activity, DollarSign } from 'lucide-react';
import './App.css';

function App() {
  // Default values set to an average California home for testing
  const [formData, setFormData] = useState({
    MedInc: 4.5,
    HouseAge: 25,
    AveRooms: 6.2,
    AveBedrms: 1.1,
    Population: 1200,
    AveOccup: 3.0,
    Latitude: 34.05,
    Longitude: -118.24
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: parseFloat(value) || '' }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error('Failed to fetch prediction from server.');
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper array to render inputs cleanly
  const formFields = [
    { name: 'MedInc', label: 'Median Income ($10k)', icon: <DollarSign size={18} /> },
    { name: 'HouseAge', label: 'House Age (Years)', icon: <Calendar size={18} /> },
    { name: 'AveRooms', label: 'Avg Rooms', icon: <DoorOpen size={18} /> },
    { name: 'AveBedrms', label: 'Avg Bedrooms', icon: <BedDouble size={18} /> },
    { name: 'Population', label: 'Block Population', icon: <Users size={18} /> },
    { name: 'AveOccup', label: 'Avg Occupancy', icon: <Home size={18} /> },
    { name: 'Latitude', label: 'Latitude', icon: <MapPin size={18} /> },
    { name: 'Longitude', label: 'Longitude', icon: <MapPin size={18} /> },
  ];

  return (
    <div className="app-container">
      <div className="header">
        <h1>California Real Estate AI</h1>
        <p>Advanced machine learning pipeline for accurate property valuations.</p>
      </div>

      <div className="prediction-card">
        <form onSubmit={handlePredict}>
          <div className="form-grid">
            {formFields.map((field) => (
              <div className="input-group" key={field.name}>
                <label>
                  {field.icon}
                  {field.label}
                </label>
                <input
                  type="number"
                  step="any"
                  name={field.name}
                  value={formData[field.name]}
                  onChange={handleInputChange}
                  required
                />
              </div>
            ))}
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? <Activity className="animate-spin" /> : <Home />}
            {loading ? 'Analyzing Market Data...' : 'Generate Valuation'}
          </button>
        </form>

        {error && (
          <div style={{ color: 'red', marginTop: '1rem', textAlign: 'center' }}>
            {error} (Is your backend running?)
          </div>
        )}

        {result && (
          <div className="result-container">
            <h2>Estimated Property Value</h2>
            <p className="price-tag">${result.predicted_price.toLocaleString()}</p>
            <p className="db-id">Saved to AlwaysData MySQL (Record ID: #{result.database_id})</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;